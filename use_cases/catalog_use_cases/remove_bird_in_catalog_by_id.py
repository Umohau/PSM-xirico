from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
from sqlalchemy.exc import DatabaseError, OperationalError
import logging

from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BirdsError,  BaseDomainError
from Projeto_xirico.exc import EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)

class RemoveBirdsInCatalogById:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, id: int) -> Result[UpdateOutputDTO, BaseDomainError| BirdsError]:
        logger.debug(
            'iniciando remocao da ave no catalogo'
            )
        warnings: list[str]= list()

        try:
            logger.debug(
                'recuperando os dados da ave'
                )
            nome_cientifico= self._repo.search_id(id).get('nome_cientifico')
            logger.debug(
                'removendo a ave do catalogo'
                )
            effect= self._repo.delete(id)
        except EntityNotFoundError:
            return Err(BirdsError.BIRD_NOT_FOUND)
        except OperationalError:
            logger.critical(
                'falha na conexao com o banco de dados', exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado no banco de dados', exc_info=True
                )
            return Err(BaseDomainError.DB_ERROR)
        logger.info(
            'ave removida do catalogo com sucesso'
            )


        try:
            logger.debug(
                'registrando auditoria da operacao'
                )
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'remove_bird_in_catalog_by_id',
                detalhes= f'removeu a ave {nome_cientifico} do catalogo'
            )
            logger.debug(
                'auditoria registrada com sucesso'
                )
        except OperationalError:
            logger.warning(
                'falha ao auditar remocao da ave. falha na conexao com o banco de dados', exc_info=True
                )
            warnings.append(BaseDomainError.DB_CONECTION_ERROR)
            warnings.append(BaseDomainError.AUDIT_FAILED)
        except DatabaseError:
            logger.warning(
                'falha ao auditar remocao da ave. erro inesperado no banco de dados', exc_info=True
                )
            warnings.append(BaseDomainError.DB_ERROR)
            warnings.append(BaseDomainError.AUDIT_FAILED)
        
        
       
        return Ok(
            UpdateOutputDTO(
                warnings= warnings,
                updated_id= id,
                old_data='True',
                new_data='False',
                effect= effect
            )
        )
        