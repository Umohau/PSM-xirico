from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err, is_err, is_ok

from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.exc import PermissionDeniedError, ProtectedEntityError, EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.DTOs.orders_DTOS import OrderUpdateDTO


logger= logging.getLogger(__name__)


class UpdateQuantityBirdOfOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit
        self._warnings: list[BaseDomainError]= list()

    
    def _get_order_details(self, order_id) -> Result[dict, BaseDomainError| OrderError]:
        try:
            logger.debug('recuperando os dados do pedido')
            order= self._repo.get_order_oid(order_id) #recupera os dados do pedido
            logger.debug(
                'dados recuperados'
            )
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(order)

    def _update_quantity(self, order_id, new_quantity: dict):
        try:
            logger.debug('actualizando pedido %s', order_id)
            effect= self._repo.update(order_id= order_id, novos_dados= new_quantity) #executa a actualizacao
            logger.info('quantidade de aves do pedido: %s alterada com sucesso', order_id)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(effect)


    def _auditar(self, operator_id, order_id, old_quantity, new_quantity):
        try:
            logger.debug('process: auditando a accao')
            self._audit.auditar(
                operador= operator_id,
                operacao= 'update_quantity_bird_of_order',
                detalhes= f'''alterou a quantidade de aves do pedido: {order_id}
                            de: {old_quantity}
                            para: {new_quantity}'''
            )
            logger.debug('operacao de actualizacao concluida com sucesso')
        except Exception:
            logger.warning(
                'falha ao auditar a troca de ave de um pedido'
            )
            self._warnings.append(BaseDomainError.AUDIT_FAILED)


    def execute(self, dados: OrderUpdateDTO):
        logger.debug(
            'iniciando operacao de troca de quantidade de aves do pedidio'
        )

        #recupera os dados do pedido
        order_id= dados.order_id
        order_= self._get_order_details(order_id) #recupera os dados do pedido
        if is_err(order_):
            return order_
        order= order_.unwrap()
        order_menager= order.get("gestor_id") #recupera o id do gestor do pedido
        operator_id= self._profile.id #guarda o id do operador logado
        order_status= order.get('estado') #guarda o estado do pedido


        #verifica a permissao para liberar edicao do pedido
        logger.debug('process: verificando permicao')
        if not order_menager == operator_id and not self._profile.ADM:
            logger.warning('permissao negada ao operador: %s para trocar a quantidade aves do pedido %s',operator_id, order_id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)
        logger.info(
            'permissao concedida ao operador %d para alterar quantidade de aves do pedido %s',
            operator_id, order_id
            )

        #verifica o estado do pedido para liberar a edicao
        logger.debug('process: verificando estado do pedido')
        if not order_status== 'pendente': 
            logger.warning('entidate protegida accao barada ao operador: %s pedidos concluidos nao podem ser editados id: %s',operator_id, order_id)
            return Err(BaseDomainError.PROTETECD_ENTITY_ERROR)

        #executa actualizacao no banco de dados
        quantity={'quantidade': dados.quantity}
        effect_= self._update_quantity(new_quantity=quantity, order_id= order_id)
        if is_err(effect_):
            return effect_
        effect= effect_.unwrap()

        #registra a accao em log de auditoria
        self._auditar(
            order_id= order_id,
            operator_id= operator_id,
            old_quantity= order['quantidade'],
            new_quantity=dados.quantity
        )

        logger.debug(
            'retornando resultado da operacao'
        )
        return Ok(
            UpdateOutputDTO(
                warnings= self._warnings,
                updated_id= order_id,
                effect= effect,
                old_data= str(order['quantidade']),
                new_data= str(dados.quantity)
            )
        )
    