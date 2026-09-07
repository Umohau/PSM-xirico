from __future__ import annotations
from typing import TYPE_CHECKING, List
import logging
from sqlalchemy.exc import OperationalError, DatabaseError
from result import Result, Ok, Err, is_err, is_ok

from Projeto_xirico.DTOs.shipment_DTO import RegistShipmentDTO
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO, UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.exc import PermissionDeniedError, ProtectedEntityError, EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.repositories.shipment_repository import ShipmentRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria, Autenticacao


logger= logging.getLogger(__name__)


class DoneOrder:
    def __init__(self,
        order: OrdersRepository,
        profile: Profile,
        audit: Auditoria,
        shipment: ShipmentRepository
    ):
        self._order= order
        self._profile= profile
        self._audit= audit
        self._shipment= shipment
        self._shipment_id= None
        self._warnings: list[BaseDomainError]= list()


    def _regist_shiment(self, processo: dict, order_id) -> Result[int, BaseDomainError]:
        try:
            logger.debug('registrando o processo da exportacao do pedido %s', order_id)
            id_gerado= self._shipment.insert(processo)
            self._shipment_id= id_gerado
            logger.info('shipment do pedido: %s foi registrado com id: %s', id)
        except DatabaseError:
                logger.critical(
                    'erro inesperado com o banco de dados ao registrar exportacao', exc_info=True
                    )
                return Err(BaseDomainError.DB_ERROR)
        return Ok(id_gerado)


    def _reveret_shipment(self) -> Result[bool, BaseDomainError]:
        try:
            logger.debug('revertendo a exportacao')
            self._shipment.delete(id= self._shipment_id)
            logger.info(
                'exportacao revertida com sucesso'
            )
        except EntityNotFoundError:
            logger.warning(
                'falha na reversao da exportacao, nao encontrada '
            )
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except DatabaseError:
            logger.critical(
                'erro inesperado com o banco de dados ao reverter a exportacao id:%d', self._shipment_id
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(True)


    def _recovery_menager_id(self, order_id) -> Result[int, BaseDomainError| OrderError]:
        try:
            logger.debug(
                'recuperando o gestor do pedido'
            )
            menager: int= self._order.get_order_oid(order_id).get('gestor_id')
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(menager)


    def _set_order_status(self, order_id, done: dict) -> Result[int, BaseDomainError]:
        try:
            logger.debug('actualizando o estado do pedido %s', order_id)
            effect= self._order.update(order_id= order_id, novos_dados= done)
            logger.info('pedido: %s actualizado com sucesso', order_id)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados ao tentar actualizar pedido id: %s', order_id, exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(effect)

    def _auditar(self, order_id):
        try:
            logger.debug('process: auditando a accao')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'done_order',
                detalhes= f'concluiu o pedido: {order_id}'
            )
            logger.debug('pedido concluido com sucesso')
        except Exception:
            logger.warning(
                'falha inesperada ao auditar accao de conclusao de pedido', exc_info=True
            )
            self._warnings.append(BaseDomainError.AUDIT_FAILED)

        
    def execute(self, dados:RegistShipmentDTO) -> Result[InsertOutputDTO, BaseDomainError| OrderError] :
        logger.debug(
            'iniciando operacao de conclusao do pedido id: %s', dados.order_id
        )
       
        order_id= dados.order_id
        done: dict= {'enviado_at': dados.sent_at, 'estado': 'concluido'}
        shipment: dict= {'order_id': order_id, 'processo_docs': dados.process_docs}

        #recupera o id do gestor do pedido
        menager=self._recovery_menager_id(order_id)
        if is_err(menager):
            return menager
        logger.debug(
            'verificando permicao para concluir o pedido'
        )

        # verifica a permicao
        if not self._profile.ADM and not self._profile.id == menager.unwrap():
            logger.warning(
                'permicao negada ao operador %d para concluir o pedido: %s', self._profile.id, order_id
            )
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)
        logger.debug(
            'permicao concedida ao operador: %d', self._profile.id
        )

        #insere a exportacao no banco de dados
        id_gerado= self._regist_shiment(processo= shipment, order_id= order_id)
        if is_err(id_gerado):
            return id_gerado

        #actualiza o estado do pedido
        effect= self._set_order_status(order_id= order_id, done= done)
        if is_err(effect):
            recovery=self._reveret_shipment()
            if is_err(recovery):
                self._warnings.append(BaseDomainError.ORPHAN_DATA_ERROR)

        #audita a operacao
        self._auditar(order_id)

        logger.debug(
            'retornando resultado da operacao'
        )
        return Ok(
            InsertOutputDTO(
            genereted_id= id_gerado.unwrap(),
            warnings= self._warnings
            )
        )
    