from __future__ import annotations
from typing import TYPE_CHECKING, List
from result import Result, Ok, Err
import logging

from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.DTOs.orders_DTOS import OrderGetResponseDTO 
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.exc import EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrderRepository

logger= logging.getLogger(__name__)


class ListOperatorMenagedOrders:
    def __init__(self, repo: OrderRepository):
        self._repo= repo


    def execute(self, operator_id: int) -> Result[List[OrderGetResponseDTO], BaseDomainError]:
        logger.debug('buscando pedidos gerenciados pelo operador: %s', operator_id)
        try:
            orders: list[dict]= self._repo.get_order_gid(operator_id)
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperados com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
         
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