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


class ChangeOrderClient:
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

    def _update_cliente(self, order_id: str, cliente:dict) ->Result[int, BaseDomainError]:
        try:
            logger.debug('actualizando pedido %s', order_id)
            effect= self._repo.update(order_id= order_id, novos_dados= cliente) #executa a actualizacao
            logger.info('cliente do pedido: %s alterado com sucesso', order_id)
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


    def _auditar(self, operator_id, order_id, new_client_id, old_client_id):
        try:
            logger.debug('auditando a accao')
            self._audit.auditar(
                operador= operator_id,
                operacao= 'change_order_client',
                detalhes= f'''alterou o cliente do pedido: {order_id}
                                de: {old_client_id}
                                para: {new_client_id}'''
            )
            logger.info(
                'operacao de troca de cliente do pedido auditado com sucesso'
            )
        except Exception:
            logger.warning(
                'falha ao registrar auditoria da operacao de troca de cliente do pedido'
            )
            self._warnings.append(BaseDomainError.AUDIT_FAILED)


    def execute(self, dados:OrderUpdateDTO ) -> Result[UpdateOutputDTO, BaseDomainError| OrderError]:
        logger.debug('recuperando os dados do pedido')
        order_id= dados.order_id
        order_= self._get_order_details(order_id) #recupera os dados do pedido
        if is_err(order_):
            return order_
        order= order_.unwrap()
        order_menager= order.get("gestor_id") #recupera o id do gestor do pedido
        operator_id= self._profile.id #guarda o id do operador logado
        order_status= order.get('estado') #guarda o estado do pedido

        #monta dados do update
        client={'cliente_id': dados.client_id}

        #verifica a permissao para liberar edicao do pedido
        logger.debug('process: verificando permicao')
        if not order_menager == operator_id and not self._profile.ADM:
            logger.warnig('permissao negada ao operador: %s para trocar o cliente do pedido %s',operator_id, order_id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)

        
        #verifica o estado do pedido para liberar a edicao
        logger.debug('verificando estado do pedido')
        if not order_status== 'pendente':
            logger.debug('estado do pedido - "%s" ', order_status)
            logger.warnig('entidate protegida accao barada ao operador: %s somente pedidos pendentes podem ser editados id: %s',operator_id, order_id)
            return Err(BaseDomainError.PROTETECD_ENTITY_ERROR)
        effect_= self._update_cliente(order_id= order_id, cliente= client)
        if is_err(effect_):
            return effect_
        effect= effect_.unwrap()
            
        #registra a accao em log de auditoria
        self._auditar(
           operator_id=operator_id,
           order_id= order_id,
           new_client_id= dados.client_id,
           old_client_id= order['cliente_id']
       )
        return Ok(
            UpdateOutputDTO(
                updated_id= order_id,
                warnings=self._warnings,
                effect= effect,
                old_data=str(order['cliente_id']),
                new_data=str(dados.client_id)
            )
        )
