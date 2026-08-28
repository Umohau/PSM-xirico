from __future__ import annotations
from typing import TYPE_CHECKING, List
from result import Result, Ok, Err
from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.DTOs.shipment_DTO import ShipmentGetResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, ShipmentsError
from sqlalchemy.exc import OperationalError
import logging

logger= logging.getLogger(__name__)

if TYPE_CHECKING:
    from Projeto_xirico.repositories.shipment_repository import ShipmentRepository

class ListOperatorShipments:
    def __init__(self, repo:ShipmentRepository):
        self._repo= repo


    def execute(self, operator_id: int) ->Result[
        List[ShipmentGetResponseDTO], BaseDomainError| ShipmentsError] :
        logger.debug(
            'busacando exportacoes do operador: %s', operator_id
        )
        try:
            shipments: List[dict]= self._repo.get_shipments_gid(operator_id)
        except EntityNotFoundError:
           return Err(ShipmentsError.SHIPMENT_NOT_FOUND_ERROR)
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
        return Ok([
            ShipmentGetResponseDTO(
                order_id= shipment['order_id'],
                process_docs=shipment['process_docs'],
                shipment_id= shipment['exportacao_id']
            ) for shipment in  shipments
        ])