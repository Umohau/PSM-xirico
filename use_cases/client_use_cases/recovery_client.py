from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging

from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class RecoveryClient:
    def __init__(
            self,
            repo: ClientsRepository,
            profile: Profile,
            audit: Auditoria
        ):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, email: str) -> Result[UpdateOutputDTO, BaseDomainError| ClientError]:
        logger.debug(
            'iniciando processo de restauracao dos dados do cliente'
        )
        warnings: list[BaseDomainError]= list()
        try:
            logger.debug(
                'restaurando os dados do cliente'
            )
            effect= self._repo.reactivate(email)
            logger.info(
                'cliente rerstaurado com sucesso'
            )
            logger.debug(
                'recuprrando id do cliente'
                )
            id= self._repo.search_email(email).get('id')
            logger.debug(
                'id recuperado %s', id
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
        
        try:
            logger.debug(
                'auditando operacao de restauracao do cliente'
            )
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'recovery_client',
                detalhes= 'recuperou o cliente com id {id}'
            )
            logger.debug(
                'operacao auditada com sucesso'
            )
        except Exception:
            logger.warning(
                'falha ao registrar log de auditoria em operacao de restauracao', exc_info= True
            )
            warnings.append(BaseDomainError.AUDIT_FAILED)

        logger.debug(
            'retornando resultado da operacao'
        )
        return Ok(
            UpdateOutputDTO(
                warnings= warnings,
                updated_id= id,
                effect= effect,
                old_data='False',
                new_data='True'
            )
        )