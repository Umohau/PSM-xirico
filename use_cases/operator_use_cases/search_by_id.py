from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err
from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.DTOs.operator_DTOs import OperatorGetByAdmResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class SearchByID:
    def __init__(
        self,
        profile: Profile,
        repo: OperatorRepository,
        audit: Auditoria 
    ):
        self._profile= profile
        self._repo= repo
        self._audit= audit
    

    def execute(self, id: int) -> Result[OperatorGetByAdmResponseDTO, BaseDomainError]:
        if not self._profile.ADM:
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)
        try:
            logger.debug(
                'buscando o operador id: %s', id
            )
            operator= self._repo.search_id(id)
        except OperationalError:
            logger.critical('falha ao conectar com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error('erro inesperado com o banco de dados', exc_info= True)
            return Err(BaseDomainError.DB_ERROR)
        logger.info(
            'busca do operador de id %s com exito', id
        )
        if operator.get('ADM') == True:
            roll= 'ADM'
        else:
            roll= 'OPR'
        return Ok(
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
            
        