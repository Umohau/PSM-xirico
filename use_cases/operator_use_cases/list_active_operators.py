from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging

from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.DTOs.operator_DTOs import OperatorGetByAdmResponseDTO, OperatorGetResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError
from Projeto_xirico.exc import EmptyTableError

if TYPE_CHECKING:
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.repositories.operator_repository import OperatorRepository

logger= logging.getLogger(__name__)


class ListActiveOperators:
    def __init__(self, repo: OperatorRepository, profile: Profile, audit: Auditoria):   
        self._repo= repo
        self._profile= profile
        self._audit= audit
    

    def execute(self) -> Result[OperatorGetByAdmResponseDTO| OperatorGetResponseDTO, BaseDomainError]:
        logger.debug(
            'buscando todos operadores activos'
        )
       
        operator_dto= list()

        try:
            operators=self._repo.search_all()
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

        logger.info('a busca retornou %s resultados', len(operators))
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
                    BI= operator['identificacao']
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