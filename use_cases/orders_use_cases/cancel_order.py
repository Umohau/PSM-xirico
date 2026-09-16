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

logger= logging.getLogger(__name__)


class CancelOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit
        self._warnings: list[BaseDomainError]= list()


    def _get_order_details(self, order_id:str) -> Result[dict, BaseDomainError| OrderError]:
        logger.debug('recuperando os dados do pedido')
        try:
            order= self._repo.get_order_oid(order_id)
            logger.info(
                'dados do pedido %s recuperados', order_id
            )
        except EntityNotFoundError:
            logger.warning(
                'pedido %s nao encontrado', order_id
            )
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except DatabaseError:
            logger.error(
                'érro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(order)


    def _auditar(self, operator_id: int, order_id: str):
        logger.debug('process: auditando a accao')
        try:
            self._audit.auditar(
                operador= operator_id,
                operacao= 'cancel_order',
                detalhes= f'cancelou o pedido id: {order_id}'
            )
            logger.info(
                'operacao  de cancelamento de pedido auditada com sucesso'
            )
        except Exception:
            logger.warning(
                'falha ao auditar operacao de cancelamento de pedido'
            )
            self._warnings.append(BaseDomainError.AUDIT_FAILED)


    def _cancel_order(self, order_id: str, cancel: dict) -> Result[int, BaseDomainError]:
        try:
            logger.debug('cancelando pedido %s', order_id)
            effect= self._repo.update(order_id= order_id, novos_dados= cancel) #executa a actualizacao
            logger.info('pedido: %s cancelado com sucesso', order_id)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return  Ok(effect)


    def execute(self, order_id: str) -> int:
        cancel={'status': 'cancelado'}
        #recupera os dados do pedido
        order_= self._get_order_details(order_id)
        if is_err(order_):
            return order_
        order= order_.unwrap()
        order_menager= order.get("gestor_id") #recupera o id do gestor do pedido
        operator_id= self._profile.id #guarda o id do operador logado
        order_status= order.get('estado') #guarda o estado do pedido

        #verifica a permissao para liberar cancelamento do pedido
        logger.debug('verificando permicao')
        if not order_menager == operator_id and not self._profile.ADM:
            logger.warning('permissao negada ao operador: %s para cancelar o pedido %s',operator_id, order_id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)
        logger.info(
            'permissao concedida para cancelar pedido %s', order_id
        )

        #verifica o estado do pedido para liberar o cancelamento
        logger.debug('verificando estado do pedido')
        if not order_status== 'pendente': 
            logger.warnig(
                'entidate protegida accao barada ao operador: %s somente pedidos pendentes podem ser cancelados order_id: %s',
                operator_id, order_id
                )
            return Err(BaseDomainError.PROTETECD_ENTITY_ERROR)

        #cancela o pedido
        effect_= self._cancel_order(order_id= order_id, cancel= cancel)
        if is_err(effect_):
            return effect_
        effect= effect_.unwrap()

        #registra a accao em log de auditoria
        self._auditar(order_id= order_id, operator_id= operator_id)
        
        logger.debug('operacao de cancelamento concluida com sucesso')
        return Ok(
            UpdateOutputDTO(
                new_data='canceled',
                old_data='pending',
                updated_id= order_id,
                effect=effect,
                warnings= self._warnings
            )
        )
