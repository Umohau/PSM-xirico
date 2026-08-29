from __future__ import annotations
from typing import TYPE_CHECKING

from result import Result, Ok, Err
import logging
from sqlalchemy.exc import  OperationalError, DatabaseError

from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.DTOs.client_DTOs import ClientUpdateDTO

logger= logging.getLogger(__name__)


class DeleteClientById:
    def __init__(
            self,
            repo: ClientsRepository,
            profile: Profile,
            audit: Auditoria
        ):
        self._repo= repo
        self._profile= profile
        self._audit= audit

    def execute(self, id: int) -> Result[UpdateOutputDTO, BaseDomainError| ClientError]:
        logger.debug(
            'iniciando operacao de exclusao do cliente'
        )
        warnings: list[BaseDomainError]= list()
        try:
            logger.debug(
                'excluindo cliente %d', id
            )
            effect= self._repo.delete(id)
            logger.info(
                'cliente id:%d excluido com sucesso', id
            )
        except EntityNotFoundError:
            return Err(ClientError.CLIENT_NOT_FOUND_ERROR)
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
        
        try:
            logger.debug('auditando a accao de exclusao do cliente')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'delete_operator_by_id',
                detalhes= f'deletou o cliente com id {id}'
            )
            logger.debug(
                'auditoria registrada com sucesso'
            )
        except Exception:
            logger.warning(
                'falha no registro de auditoria da operacao de exclusao do cliente',
                exc_info=True
            )
            warnings.append(BaseDomainError.AUDIT_FAILED)

        logger.debug(
            'retornando resultado da actualizacao'
        )
        return Ok(
            UpdateOutputDTO(
                warnings= warnings,
                updated_id=id,
                old_data='True',
                new_data= 'False',
                effect=effect
            )
        )
    