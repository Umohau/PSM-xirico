from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err
from sqlalchemy.exc import DatabaseError, OperationalError

from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.DTOs.bird_DTOs import BirdsUpdateDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, BirdsError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class UpdateBirdCientificNameInCatalog:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, dados_in: BirdsUpdateDTO) -> Result[UpdateOutputDTO, BaseDomainError| BirdsError]:
        logger.debug('iniciando actualizacao do nome cientifico da ave')
        dado= {'nome_cientifico': dados_in.cientific_name}
        warnings: list[str]= list()

        try:
            logger.debug('recuperando o nome cientifico actual da ave')
            nome_anterior= self._repo.search_id(dados_in.bird_id).get('nome_cientifico')  # recupera o nome cientifico actual
            logger.debug('actualizando o nome cientifico da ave')
            effect= self._repo.update(dados= dado, id= dados_in.bird_id) # actualiza o nome cientifico
        except EntityNotFoundError:
            return Err(BirdsError.BIRD_NOT_FOUND)
        except OperationalError:
            logger.critical(
                'erro na conexao do banco de dados',  exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error('erro no banco de dados ao actualizar nome cientifico da ave', exc_info=True)
            return Err(BaseDomainError.DB_ERROR)
        logger.info('nome cientifico da eve id %s actualizado com sucesso', dados_in.bird_id)


        # regiatra log de auditoria
        try:
            logger.debug('registrando a actualizacao no log de auditoria')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'update_bird_cientific_name_in_catalog',
                detalhes= f"actualizou o nome cientifico da ave id {id} de {nome_anterior} para {dados_in.cientific_name}"
            )
            logger.debug('auditoria registrada com sucesso')   
        except OperationalError:
            logger.warning(
                'falha na conexao do banco de dados', exc_info=True
                )
            warnings.append(BaseDomainError.DB_CONECTION_ERROR)
            warnings.append(BaseDomainError.AUDIT_FAILED)
        except DatabaseError:
            logger.warning('falha no registro de auditoria ao actualizar nome cientifico da ave', exc_info=True)
            warnings.append(BaseDomainError.AUDIT_FAILED)
            warnings.append(BaseDomainError.DB_ERROR)
        
        
        return Ok(
             UpdateOutputDTO(
                updated_id=dados_in.bird_id,
                new_data= dados_in.cientific_name,
                old_data= nome_anterior,
                effect=effect,
                warnings= warnings
            )
        )