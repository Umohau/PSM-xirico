from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err, is_err

from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.exc import PermissionDeniedError, ProtectedEntityError, EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class DeleteOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit
        self._warnings: list[BaseDomainError]= list()


    
    def _recovery_menager_id(self, order_id) -> Result[int, BaseDomainError| OrderError]:
        try:
            logger.debug(
                'recuperando o gestor do pedido'
            )
            menager: int= self._repo.get_order_oid(order_id).get('gestor_id')
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(menager)


    def _exclude_order(self, order_id):
        try:
            logger.debug('process: deletando o pedido: %s', order_id)
            effect= self._repo.delete(order_id)
            logger.info('pedido: %s excluido com sucesso', order_id)
        except ProtectedEntityError:
            logger.warning('entidade protegida accao de delecao barada')
            return Err(BaseDomainError.PROTETECD_ENTITY_ERROR)
        except OperationalError:
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            return Err(BaseDomainError.DB_ERROR)
        return Ok(effect)



    def _auditar(self, order_id, order_menager):
        try:
            logger.debug('process: auditando a accao')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'delete_order',
                detalhes= f'eliminou o pedido id: {order_id}, gerenciado por {order_menager}'
            )
            logger.debug('sucess: processo de exclusao concluido')
        except Exception:
            logger.warning(
                'erro insperado ao auditar operacao de exclusao do pedido: %s', order_id
            )
            self._warnings.append(BaseDomainError.AUDIT_FAILED)


    def execute(self, order_id: str) -> Result[UpdateOutputDTO, BaseDomainError| OrderError]:
        # recupera o id do gestor do pedido
        order_menager= self._recovery_menager_id(order_id= order_id)
        if is_err(order_menager):
            return order_menager
        menager_id= order_menager.unwrap()

        #verifica a permicao para liberar a delecao
        logger.debug('process: verificando permicao')
        if not menager_id == self._profile.id and not self._profile.ADM:
            logger.warnig('permissao negada para excluir o pedido: %s', order_id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)

        #exclue o pedido do banco de dados
        effect_= self._exclude_order(order_id= order_id)
        if is_err(effect_):
            return effect_
        effect= effect_.unwrap()

        # audita a operacao
        self._auditar(order_id=order_id, order_menager= order_menager)

        logger.debug(
            'retornando os resultados'
        )
        return Ok(
           UpdateOutputDTO(
               warnings= self._warnings,
               updated_id= order_id,
               new_data='None',
               old_data='None',
               effect= effect
           )
       )
        