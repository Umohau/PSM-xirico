from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging
from sqlalchemy .exc import OperationalError, DatabaseError

from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.exc import EntityNotFoundError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.repositories.messageBox_repository import  messageBoxRepository
    from Projeto_xirico.seguranca import Autententicacao,  Auditoria
    from Projeto_xirico.profile import Profile

logger= logging.getLogger(__name__)


class DisableOperatorByID:
    def __init__(
        self,
        repo: OperatorRepository,
        message_box: messageBoxRepository,
        profile: Profile,
        audit: Auditoria
        ):
        self._repo= repo
        self._message_box= message_box
        self._profile= profile
        self._audit= audit
        
        
    def execute(self, id: int) -> Result[UpdateOutputDTO, BaseDomainError| OperatorError]:
        logger.debug('iniciando processo de desativacao de operador')
        warnings: list[BaseDomainError]= list()
        logger.debug('verificando permissao')
        # verifica a permissao
        if not self._profile.ADM:
            logger.warning('permissao negada')
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)

        #recupera os dados do operador e faz a desaxtivacao
        try:
            logger.debug('recuperando os dados do operador %s', id)
            operador= self._repo.search_id(id)
            #executa e armazena o numero de deletados
            logger.debug('desactivando operador id: %s', id)
            efeito= self._repo.delete(id) 
            logger.info('operador: %s desactivado com sucesso', id)
        except EntityNotFoundError:
            logger.warning('operador nao encontrado')
            return Err(OperatorError.OPERATOR_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical('falha ao conectar com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error('Erro inesperado com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_ERROR)

        #audita a accao
        try:
            logger.debug('auditando a operacao de desactivacao')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= "disable operator",
                detalhes= f'desativou o operador id {id}')
            logger.debug('operacao auditada')
        except Exception:
            logger.warning('falha inesperada ao auditar a operacao', exc_info=True)
            warnings.append(BaseDomainError.AUDIT_FAILED)

        #adiciona uma mensagem de notificacao na caixa para envio
        try:
            logger.debug('enfileirando email de notificacao da desactivacao')
            self._message_box.add_(
                dados={
                    "to": operador.get('email'),
                    "type": 'Disable',
                    "name": operador.get('nome'),
                    "channel": 'email'
                } )
            logger.debug('email enfileirado com sucesso')
        except DatabaseError:
            logger.warning('falha inesperada ao enfileirar email', exc_info=True)
            warnings.append(BaseDomainError.MESSAGE_BOX_FAILLED)
        logger.debug('retornando resultados')

        return Ok(
            UpdateOutputDTO(
                updated_id=id,
                effect= efeito,
                new_data='False',
                old_data='True',
                warnings= warnings
            ))
