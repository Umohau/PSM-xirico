from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err

from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.DTOs.shipment_DTO import ShipmentGetResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, ShipmentsError
from Projeto_xirico.exc import EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.shipment_repository import ShipmentRepository
    from datetime import datetime

logger= logging.getLogger(__name__)


class SearchShipmentByOrderId:
    def __init__(self, repo:ShipmentRepository):
        self._repo= repo


    def execute(self, order_id: str) -> Result[
        ShipmentGetResponseDTO, 
        BaseDomainError| ShipmentsError]:
        try:
            logger.debug(
                    'buscando exportacao do pedido id: %s', order_id
                )
            shipment= self._repo.get_shipment_oid(order_id)
            logger.info(
                    'exportacao do pedido: %s localizada', order_id
                )
        except EntityNotFoundError:
            return Err(ShipmentsError.SHIPMENT_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco dedas', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)

        return Ok(
            ShipmentGetResponseDTO(
                shipment_id=shipment['exportacao_id'],
                order_id= shipment['order_id'],
                process_docs= shipment['processo_docs']
            )
        )


class SearchShipmentsByEpoc:
    def __init__(self, repo:ShipmentRepository):
        self._repo= repo
    
    
    def execute(self, data_inicio: datetime, data_limite: datetime) -> Result[
        list[ShipmentGetResponseDTO], 
        BaseDomainError| ShipmentsError]:
        try:
            logger.debug(
                'buscando exportacoes no periodo de %s a %s', data_inicio, data_limite
            )
            Shipments= self._repo.search_epoc(data_inicio= data_inicio, data_fim= data_limite)
            logger.info(
                'a busca por epoca retornou %d resultados', len(Shipments)
            )
        except EntityNotFoundError:
            return Err(ShipmentsError.SHIPMENT_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco dedas', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)

        return Ok(
            [ShipmentGetResponseDTO(
                shipment_id=shipment['exportacao_id'],
                order_id= shipment['order_id'],
                process_docs= shipment['processo_docs']
            ) for shipment in Shipments]
        )
