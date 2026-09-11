from __future__ import annotations
from typing import TYPE_CHECKING

from result import Result, Ok, Err
from sqlalchemy.exc import OperationalError, DatabaseError
import logging

from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.client_DTOs import ClientGetResponseDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class SearchClientById:
    def __init__(self,
        repo: ClientRepository,
        profile: Profile
        ):
        self._repo= repo
        self._profile= profile


    def execute(self, client_id: int) -> Result[ClientGetResponseDTO, BaseDomainError| ClientError]:
        logger.debug(
            'buscando cliente de id: %d', client_id
        )
        try:
            client= self._repo.search_by_id(client_id)
            logger.info(
                'a busca encontrou o cliente de id:%s',client_id
            )
        except EntityNotFoundError:
            return Err(ClientError.CLIENT_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info= True
            )
            return Err(BaseDomainError.DB_ERROR)
        
        logger.debug(
            'retornando resultado'
        )
        return Ok(
            ClientGetResponseDTO(
                client_id= client['id'],
                name= client['nome'],
                email= client['email'],
                domain= client['dominio'],
                telephone= client['telefone'],
                address= client['endereco']
            ) 
        )
