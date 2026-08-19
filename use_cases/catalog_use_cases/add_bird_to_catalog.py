from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
from sqlalchemy.exc import DatabaseError, OperationalError
import logging

from Projeto_xirico.DTOs.bird_DTOs import AddBirdOutPutDTO
from Projeto_xirico.domain_exceptions import BirdsError, BaseDomainError
from Projeto_xirico.exc import DuplicateError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.DTOs.bird_DTOs import BirdsAddDTO, AddBirdOutPutDTO

logger= logging.getLogger(__name__)

class AddBirdToCatolog:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._audit= audit
        self._profile= profile


    def execute(self, dados: BirdsAddDTO)-> Result[AddBirdOutPutDTO, BaseDomainError|BirdsError]:
        logger.debug('iniciando insercao da ave no catalogo')
        warnings: list[str]= list()

        try:
            logger.debug('inserindo ave %s', dados.cientific_name)
            id_gerado= self._repo.insert(dados.model_dump())
        except DuplicateError:
            return Err(BirdsError.BIRD_ALREAD_EXISTS)
        
        except OperationalError:
            logger.critical(
                'falha na conexao com o banco de dados', exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
                logger.error(
                    'falha inesperado no banco de dados', exc_info=True
                    )
                return Err(BaseDomainError.DB_ERROR)
        logger.info(
            'ave adicionada ao catalogo com sucesso'
            )
        

        try: 
            logging.debug(
                'registrando log de auditoria da insercao'
                )
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'add_bird_to_catalog',
                detalhes= f'adicionou a ave {dados.cientific_name} ao catalogo'
            )
            logger.debug(
                'auditoria registrada com sucesso'
                )
        except DatabaseError:
            logger.warning(
                'falha no registro de auditoria, ao inserir ave no catalogo', exc_info=True
                )
            warnings.append(BaseDomainError.DB_ERROR)
            warnings.append(BaseDomainError.AUDIT_FAILED)
        except OperationalError:
            logger.warning(
                'falha ao conectar com o banco de dados', exc_info=True
                )
            warnings.append(BaseDomainError.AUDIT_FAILED)
            warnings.append(BaseDomainError.DB_CONECTION_ERROR)
        

        
        return Ok(AddBirdOutPutDTO(
            warnings= warnings,
            bird_id= id_gerado
        ))
        