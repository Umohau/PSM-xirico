from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err
from sqlalchemy.exc import DatabaseError, OperationalError

from Projeto_xirico.exc import EmptyTableError
from Projeto_xirico.domain_exceptions import BaseDomainError
from Projeto_xirico.DTOs.bird_DTOs import BirdGetResponseDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository


logger= logging.getLogger(__name__)


class ShowCatalog:
    def __init__(self, repo: BirdsRepository):
        self._repo= repo
        


    def execute(self) -> Result[list[BirdGetResponseDTO], BaseDomainError]:
        logger.debug('iniciando operacao de busca')
        dtos: list[BirdGetResponseDTO]= list()

        try:
            data= self._repo.search_all()
        except EmptyTableError:
            return Err(BaseDomainError.EMPTY_TABLE)
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
