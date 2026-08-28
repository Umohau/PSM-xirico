from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging
from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.profile import Profile

logger= logging.getLogger(__name__)


class PromoteOperator:
    def __init__(
        self, 
        message_box: messageBoxRepository,
        repo: OperatorRepository,
        profile: Profile,
        audit: Auditoria
        ) :
        self._message_box= message_box
        self._repo= repo
        self._profile= profile
        self._audit= audit
            
            
    def execute(self, id: int) -> Result[UpdateOutputDTO, BaseDomainError | OperatorError]:
        logger.debug('iniciando processo de promocao de Operador')
        warnings: list[BaseDomainError]=list()

        logger.debug('verificando permissao')
        #verifica se o operdor em sessao é ADM
        if not self._profile.ADM:
            logger.warning('permissao negada para promover operador %s a administrador', id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)
        
        try:
            logger.debug('recuperando dados do operador %s', id)
            operador= self._repo.search_id(id)# revupera os dados do operador a promover
            logger.debug('executando a promocao do operador id: %s', id)
            # executa a promocao
            effect= self._repo.update(
                id,
                dados={"ADM": True})
            logger.info('operador id: %s promovido a ADM com sucesso')
        except EntityNotFoundError:
            logger.warning('operador id: %s nao encontrado', id)
            return Err(OperatorError.OPERATOR_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical('falha ao conectar com o banco de dados', exc_info= True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error('falha inesperada com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_ERROR)
       
        #audita a accao
        try:
            logger.debug('auditando a operacao de promocao')
            self._audit.auditar(
                operador= id,
                operacao= "Promote_operator",
                detalhes= f"promoveu a ADM o operador de id: {id}")
            logger.debug('operacao auditada com sucesso')
        except Exception:
            logger.warning('falha ao auditar operacao de promocao', exc_info=True)
            warnings.append(BaseDomainError.AUDIT_FAILED)

        #adiciona uma mensagem a caixa de mensagens para envio
        try:
            logger.debug('enfileirando email de notificacao')
            self._message_box.add_(
                dados={
                    "to":operador.get("email"),
                    "type":'promote',
                    "name": operador.get("nome"),
                    "channel": 'email'
                } )
            logger.debug('email enfileirado com sucesso')
        except DatabaseError:
            logger.warning('faljha ao enfileirar email de notificacao da promocao', exc_info= True)
            warnings.append(BaseDomainError.MESSAGE_BOX_FAILLED)

        return Ok(
            UpdateOutputDTO(
                warnings= warnings,
                updated_id= id,
                new_data= 'ADM: True',
                old_data='ADM: False',
                effect= effect
            )
        )
