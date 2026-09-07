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


class ChangeOrderBird:
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


    def _change_order_bird(self, order_id: str, bird:dict) -> Result[int, BaseDomainError]:
        try:
            logger.debug('actualizando pedido %s', order_id)
            effect= self._repo.update(order_id= order_id, novos_dados= bird) #executa a actualizacao
            logger.info('ave do pedido: %s alterado com sucesso', order_id)
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
        
    def _auditar(self, bird_id, new_id, order_id):
        try:
            logger.debug('auditando a accao')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'change_order_bird',
                detalhes= f'''alterou a ave do pedido: {order_id}
                                de: {bird_id}
                                para: {new_id}'''
            )
            logger.debug('operacao de actualizacao concluida com sucesso')
        except Exception:
            logger.warning(
                'falha ao auditar a troca de ave de um pedido'
            )
            self._warninigs.append(BaseDomainError.AUDIT_FAILED)

    def execute(self, dados: OrderUpdateDTO) -> Result[UpdateOutputDTO, BaseDomainError| OrderError]:
        logger.debug(
            'iniciando operacao de actualizao de ave do pedido'
        )
        order_= self._get_order_details(dados.order_id)#recupera os dados do pedido
        if is_err(order_):
            return order_
        order= order_.unwrap()
        order_menager= order.get("gestor_id") #recupera o id do gestor do pedido
        operator_id= self._profile.id #guarda o id do operador logado
        order_status= order.get('estado') #guarda o estado do pedido
        bird={'ave_id': dados.bird}

        #verifica a permissao para liberar edicao do pedido
        logger.debug(
            'verificando permicao'
            )
        if not order_menager == operator_id and not self._profile.ADM:
            logger.warnig('permissao negada ao operador: %s para trocar o cliente do pedido %s',operator_id, dados.order_id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)

        #verifica o estado do pedido para liberar a edicao
        logger.debug(
            'verificando estado do pedido'
            )
        if not order_status== 'pendente':
            logger.warnig(
                'entidate protegida accao barada ao operador: %s somente pedidos pendentes podem ser editados id: %s',
                operator_id, dados.order_id
                          )
            return Err(BaseDomainError.PROTETECD_ENTITY_ERROR)
        effect_= self._change_order_bird(order_id= dados.order_id, bird=bird)
        if is_err(effect_):
            return effect_
        effect=effect_.unwrap()

        #registra a accao em log de auditoria
        self._auditar(new_id=dados.bird, bird_id=order['ave_id'], order_id= dados.order_id)
        return Ok(
            UpdateOutputDTO(
                new_data= dados.bird,
                old_data= order['ave_id'],
                effect= effect,
                warnings= self._warnings,
                updated_id= dados.order_id
            )
        )

