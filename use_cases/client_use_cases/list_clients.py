from __future__ import annotations
from typing import TYPE_CHECKING, List

from result import Result, Ok, Err
import logging
from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.exc import EmptyTableError
from Projeto_xirico.domain_exceptions import BaseDomainError
from Projeto_xirico.DTOs.client_DTOs import ClientGetResponseDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class ListClients:
    def __init__(
        self,
        repo: ClientRepository,
        profile: Profile,
        audit: Auditoria
    ):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self) ->Result[List[ClientGetResponseDTO], BaseDomainError]:
        logger.debug(
            'buscando todos os clientes'
        )
        try:
            clients= self._repo.search_all()
            logger.info(
                'a busca retornou %d clientes', len(clients)
            )
        except EmptyTableError:
            return Err(BaseDomainError.EMPTY_TABLE)
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
