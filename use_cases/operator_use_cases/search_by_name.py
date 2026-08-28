from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging
from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.DTOs.operator_DTOs import OperatorGetResponseDTO, OperatorGetByAdmResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError
from Projeto_xirico.exc import EmptyTableError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class SearchByName:
    def __init__(
            self,
            profile: Profile,
            repo: OperatorRepository,
            audit: Auditoria
        ):
        self._profile= profile
        self._repo= repo
        self._audit= audit


    def execute(self, name: str) -> Result[
        list[OperatorGetByAdmResponseDTO|OperatorGetResponseDTO],
        BaseDomainError]:
       
        operator_dto: list[OperatorGetByAdmResponseDTO| OperatorGetResponseDTO]= list()
        try:
            logger.debug('buscando o operador com nome: %s', name)
            operators= self._repo.search_name(name)
        except EmptyTableError:
            return Err(BaseDomainError.EMPTY_TABLE)
        except OperationalError:
            logger.critical('erro ao conectar com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.debug(
                'erro inesperado com o banco de dados ', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)

        logger.info('a busca retornou %s resultados para o nome: %s ', len(operators), name)

        logger.debug('convertendo resultados para DTOS')
        for operator in operators:
            logger.debug(
                'definnindo a roll do operador'
            )
            if operator.get('ADM') == True:
                roll= 'ADM'
            else:
                roll= 'OPR'
            logger.debug(
                'definindo o DTO de retorno'
            )
            if self._profile.ADM:
                logger.debug(
                    'DTO definido para ADM'
                )
                operator_dto.append(
                    OperatorGetByAdmResponseDTO(
                    operator_id= operator['id'],
                    operator_name= operator['nome'],
                    roll= roll,
                    operator_email= operator['email'],
                    phone_number= operator['telefone'],
                    morada= operator['endereco'],
                    BI= operator['BI']
                    )
                )
            else:
                logger.debug(
                    'DTO definido para OPR'
                )
                operator_dto.append(
                    OperatorGetResponseDTO(
                    operator_id= operator['id'],
                    operator_name= operator['nome'],
                    roll= roll
                    )
                )

        logger.debug('retornando  os resultados')
        return Ok(operator_dto)