from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging

from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.exc import DuplicateError
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO



if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.DTOs.client_DTOs import ClientRegistDTO


logger= logging.getLogger(__name__)


class RegistNEwClient:
    def __init__(self,
        repo: ClientRepository,
        audit: Auditoria,
        profile: Profile
        ):
        self._repo= repo
        self._audit= audit
        self._profile= profile


    def execute(self, dados: ClientRegistDTO) -> Result[InsertOutputDTO, BaseDomainError| ClientError]:
        logger.debug(
            'iniciando cadastro do cliente %s', dados.name
        )
        warnings: list[BaseDomainError]=list()
        try:
            logger.debug('persistindo os dados')
            id_gerado= self._repo.insert(dados)
            logger.info(
                'cliente %s registrado com id: %s', dados.name, id_gerado
            )
        except DuplicateError:
            return Err(ClientError.CLIENT_ALREAD_EXISTS_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado  com o banco de dados', exc_info= True
            )
            return Err(BaseDomainError.DB_ERROR)
        try:
            logger.debug(
                'registrando auditoria da operacao de registro do cliente %s', id_gerado
            )
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'regist_new_client',
                detalhes= f"registou o cliente com id {id_gerado}"
            )
        except Exception:
            logger.warning(
                'falha ao auditar operacao de registro do cliente', exc_info=True
            )
            warnings.append(BaseDomainError.AUDIT_FAILED)
        logger.debug(
            'retornando resultado da operacao'
        )
        return Ok(
            InsertOutputDTO(
                warnings=warnings,
                genereted_id=id_gerado
            )
        )