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


class ClientUpdateAdressById:
    def __init__(
            self,
            repo: ClientsRepository,
            profile: Profile,
            audit: Auditoria
        ):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, dados: ClientUpdateDTO) -> Result[UpdateOutputDTO, BaseDomainError| ClientError]:
        logger.debug(
            'iniciando processo de actualizacao de endereco do cliente %s', dados.client_id
        )
        new_address: dict= {'endereco': dados.address}
        warnings: list[BaseDomainError]= list()

        try:
            logger.debug(
                'recuperando o endereco actual'
            )
            old_address:str= self._repo.search_id(dados.client_id).get('endereco')
            logger.debug(
                'actualizando o endereco'
            )
            effect=self._repo.update(dados_= new_address, id= dados.client_id)
            logger.info(
                'endereco do cliente %s actualizado com sucesso', dados.client_id
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
            logger.debug('auditando a accao de actualizacao de endereco do cliente')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'client_update_adress_by_id',
                detalhes= f'actualizou o endereço do cliente com id {dados.client_id}'
            )
            logger.debug(
                'auditoria registrada com sucesso'
            )
        except Exception:
            logger.warning(
                'falha no registro de auditoria da operacao de actualizacao de endereco do cliente',
                exc_info=True
            )
            warnings.append(BaseDomainError.AUDIT_FAILED)

        logger.debug(
            'retornando resultado da actualizacao'
        )
        return Ok(
            UpdateOutputDTO(
                warnings= warnings,
                updated_id=dados.client_id,
                old_data=old_address,
                new_data= dados.address,
                effect=effect
            )
        )
    