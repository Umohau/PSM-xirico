from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging
from sqlalchemy.exc import DatabaseError, OperationalError

from Projeto_xirico.domain_exceptions import BirdsError, BaseDomainError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class RecoveryBirdInCtalog:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, id: int) -> Result[UpdateOutputDTO, BaseDomainError| BirdsError]:
        warnings: list[str]= list()
        try:
            effect= self._repo.recovery(id)
        except EntityNotFoundError:
            return Err(BirdsError.BIRD_NOT_FOUND)
        except OperationalError:
            logger.critical('falha na conexao com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)

        except DatabaseError:
            logger.error('erro inesperado no banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_ERROR)
        
        try:
            logger.debug(
                'auditando a operacao'
                )
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'recovery_bird_in_catalog',
                detalhes= f'restaurou a ave de id {id} para o catalogo'
            )
            logger.debug(
                'auditoria registrada com sucesso'
            )
        except OperationalError:
            logger.warning(
                'falha ao auditar restauracao da ave. falha na conexao com o banco de dados', exc_info=True
                )
            warnings.append(BaseDomainError.DB_CONECTION_ERROR)
            warnings.append(BaseDomainError.AUDIT_FAILED)
        except DatabaseError:
            logger.warning(
                'falha ao auditar restauracao da ave. erro inesperado no banco de dados', exc_info=True
                )
            warnings.append(BaseDomainError.DB_ERROR)
            warnings.append(BaseDomainError.AUDIT_FAILED)
       

        return Ok(
            UpdateOutputDTO(
                updated_id= id,
                warnings= warnings,
                effect= effect,
                new_data='True',
                old_data='False'

            )
        )