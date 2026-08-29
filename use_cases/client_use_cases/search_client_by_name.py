from __future__ import annotations
from typing import TYPE_CHECKING, List

from result import Result, Ok, Err
from sqlalchemy.exc import OperationalError, DatabaseError
import logging

from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.client_DTOs import ClientGetResponseDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class SearchClietByName:
    def __init__(self,
        repo: ClientsRepository,
        audit: Auditoria,
        profile: Profile
        ):
        self._repo= repo
        self._audit= audit
        self._profile= profile


    def execute(self, name: str) -> Result[List[ClientGetResponseDTO], BaseDomainError| ClientError]:
        logger.debug(
            'buscando cliente com nome: %s', name
        )
        try:
            clients= self._repo.search_name(name)
            logger.info(
                'a busca encontrou %d clientes para o nome: %s', len(clients), name
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
            'retornando resultados'
        )
        return Ok(
            [ClientGetResponseDTO(
                client_id= client['id'],
                name= client['nome'],
                email= client['email'],
                domain= client['dominio'],
                telephone= client['telefone'],
                address= client['endereco']
            ) for client in clients]
        )
