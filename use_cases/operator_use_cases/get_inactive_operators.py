from __future__ import annotations
from typing import TYPE_CHECKING, List
from result import Result, Ok, Err
import logging

from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.DTOs.operator_DTOs import OperatorGetByAdmResponseDTO
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class GetInactiveOperators:
    def __init__(
        self,
        repo: OperatorRepository,
        profile: Profile
        ):
        self._repo= repo
        self._profile= profile


    def execute(self) -> Result[
        List[OperatorGetByAdmResponseDTO],
        BaseDomainError | OperatorError]:

        logger.debug('iniciando busca de inactivos')
        logger.debug('verificando permissao')
        if not self._profile.ADM:
            logger.warning('permissao negada ao operador: %s para listar inaactivos', self._profile.id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)
        inactives_dtos: list[OperatorGetByAdmResponseDTO]= list()

        try:
            logger.debug('buscando operadores inactivos')
            inactives:list[dict]= self._repo.get_inactives()
            logger.info('busca de inactivos retornou %s resultados', len(inactives))
        except OperationalError:
            logger.critical('falha ao conectar com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error('erro inesperado no banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_ERROR)

        if len(inactives)==0:
            return Err(OperatorError.OPERATOR_NOT_FOUND_ERROR)
        
        logger.debug('convertendo resposta em DTOs')
        for inactive in inactives:
            if inactive.get('ADM') == True:
                roll= 'ADM'
            else:
                roll= 'OPR'
            inactives_dtos.append(
                OperatorGetByAdmResponseDTO(
                operator_id= inactive['id'],
                operator_name= inactive['nome'],
                roll= roll,
                operator_email= inactive['email'],
                phone_number= inactive['telefone'],
                morada= inactive['endereco'],
                BI= inactive['BI']
                )
            )
        return Ok(inactives_dtos)
    