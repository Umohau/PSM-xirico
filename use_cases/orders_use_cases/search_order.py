from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err

from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.DTOs.orders_DTOS import OrderGetResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.exc import EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository

logger= logging.getLogger(__name__)


class SearcbOrdersByOrderId:
    def __init__(self, repo: OrdersRepository):
        self._repo= repo


    def execute(self, order_id: str) -> Result[OrderGetResponseDTO, BaseDomainError| OrderError]:
        try:
            order= self._repo.search_oid(order_id)
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info= True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        
        return Ok(
            OrderGetResponseDTO(
                id= order['order_id'],
                date_of_regist= order['registado_at'],
                sent_date=order['enviado_at'],
                menager_id= order['gestor_id'],
                client_id= order['cliente_id'],
                quantity= order['quantidade'],
                bird=order['ave_id'],
                order_status= order['estado']
            )
        )