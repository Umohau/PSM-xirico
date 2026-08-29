from __future__ import annotations
from typing import TYPE_CHECKING, List

from result import Result, Ok, Err
import logging
from sqlalchemy.exc import  OperationalError, DatabaseError

from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.DTOs.orders_DTOS import OrderGetResponseDTO

logger= logging.getLogger(__name__)


if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository

class ListClientOrders:
    def __init__(self, repo: OrdersRepository):
        self._repo= repo


    def execute(self, client_id: int) -> Result[List[OrderGetResponseDTO], BaseDomainError| OrderError]:
        logger.debug(
            'buscando pedidos do cliente %d', client_id
        )
        try:
            orders=self._repo.get_orders_cid(client_id)
            logger.info(
                'a busca por exportacoes  do cliente id:%d encontrou %d resultados', client_id, len(orders)
            )
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        logger.debug(
            'retornando resultados'
        )
        return Ok(
            [
                OrderGetResponseDTO(
                id= order['order_id'],
                date_of_regist= order['registado_at'],
                sent_date= order['enviado_at'],
                client_id= order['cliente_id'],
                menager_id= order['gestor_id'],
                quantity= order['quantidade'],
                bird= order['bird_id'],
                order_status= order['status']
            ) for order in orders
            ]
        )
