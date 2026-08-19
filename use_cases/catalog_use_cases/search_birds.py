from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err
from sqlalchemy.exc import DatabaseError, OperationalError

from Projeto_xirico.DTOs.bird_DTOs import BirdGetResponseDTO
from Projeto_xirico.domain_exceptions import BirdsError, BaseDomainError
from Projeto_xirico.exc import EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository


logger= logging.getLogger(__name__)


class SearchBirdByName:
    def __init__(self, repo: BirdsRepository):
        self._repo= repo
            
    
    
    def execute(self, nome: str) -> Result[list[BirdGetResponseDTO], BaseDomainError| BirdsError]:
        logger.debug(
            'buscando a ave pelo nome'
            )
        dtos: list[BirdGetResponseDTO]= list()

        try:
            data= self._repo.search_name(nome)
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
        
        logger.info('busca realizada com exito')


        logger.debug('montando DTOs de retorno')
        for data_bird in data:
            dtos.append(
                BirdGetResponseDTO(
                    bird_id= data_bird['id'],
                    usual_name= data_bird['nome_comum'],
                    cientific_name=data_bird['nome_cientifico'],
                    bird_species=data_bird['especie'],
                    bird_price= data_bird['preco'],
                    status='disponivel'
                )
            )
        logger.debug('retornando resultado')
        return Ok(
            dtos
        )



class SearchBirdById:
    def __init__(self, repo: BirdsRepository):
        self._repo= repo
            
    
    
    def execute(self, id: int) -> Result[BirdGetResponseDTO, Err]:
        logger.debug('buscando ave pelo id')
        try:
            data_bird= self._repo.search_id(id)
        except EntityNotFoundError:
            return Err(BirdsError.BIRD_NOT_FOUND)
        except OperationalError:
            logger.critical('falha ao tentar conectar com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error('erro inesperado com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_ERROR)
        logger.info('busca realizada com sucesso')
        logger.debug('retornando o resultado')
       
        return Ok(
            BirdGetResponseDTO(
                bird_id= data_bird['id'],
                usual_name= data_bird['nome_comum'],
                cientific_name=data_bird['nome_cientifico'],
                bird_species=data_bird['especie'],
                bird_price= data_bird['preco'],
                status='disponivel'
                )
            )
    