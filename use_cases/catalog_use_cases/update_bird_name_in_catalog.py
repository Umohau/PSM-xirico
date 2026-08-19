from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from result import Err, Ok, Result
from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.DTOs.bird_DTOs import BirdsUpdateDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, BirdsError
from Projeto_xirico.exc import EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.seguranca import Auditoria

logger = logging.getLogger(__name__)


class UpdateBirdNameInCatalogById:

    def __init__(
        self, repo: BirdsRepository, profile: Profile, audit: Auditoria
    ):
        self._repo = repo
        self._profile = profile
        self._audit = audit

    def execute(self, dados: BirdsUpdateDTO) -> Result[UpdateOutputDTO, BirdsError | BaseDomainError]:
        logger.debug("iniciando a actualizacao do nome da ave no catalogo")
        dado = {"nome_comum": dados.usual_name}
        warnings: list[str] = list()

        # Recupera o nome actual da ave e actualiza o nome comum
        try:
            logger.debug("recuperando o nome actual da ave")
            bird_data = self._repo.search_id(dados.bird_id)
            nome_anterior = bird_data.get("nome_comum")

            logger.debug("actualizando o nome comum da ave")
            effect = self._repo.update(dados=dado, id=dados.bird_id)
        except EntityNotFoundError:
            return Err(BirdsError.BIRD_NOT_FOUND)
        except OperationalError:
            logger.critical(
                'erro na conexao do banco de dados',  exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        
        except DatabaseError :
            logger.error(
                "erro inesperado ao actualizar nome da ave", exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        
        logger.info(
            "nome comum da ave id %s actualizado com sucesso", dados.bird_id
        )

        # Regista o log de auditoria da acção
        try:
            logger.debug(
                "registando o log de auditoria da actualizacao"
                )
            self._audit.auditar(
                operador=self._profile.id,
                operacao="update_bird_name_in_catalog_by_id",
                detalhes=(
                    f'actualizou o nome da ave id {dados.bird_id} de'
                    f' "{nome_anterior}" para "{dados.usual_name}"'
                ),
            )
            logger.debug(
                'actualizacao auditada com sucesso'
                )
        except OperationalError:
            logger.warning(
                'falha na conexao do banco de dados', exc_info=True
                )
            warnings.append(BaseDomainError.DB_CONECTION_ERROR)
            warnings.append(BaseDomainError.AUDIT_FAILED)
        except DatabaseError:
            logger.warning(
                "falha no registro de auditoria ao actualizar nome da ave no"
                " catalogo",
                exc_info=True,
            )
            warnings.append(BaseDomainError.AUDIT_FAILED)
            warnings.append(BaseDomainError.DB_ERROR)
       
       
        logger.debug(
            "retornando o resultado"
            )
        return Ok(
            UpdateOutputDTO(
                warnings=warnings,
                updated_id=dados.bird_id,
                old_data=nome_anterior,
                new_data=dados.usual_name,
                effect=effect,
            )
        )
