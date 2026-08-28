from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok, Err
import logging

from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import OperationalError, DatabaseError


from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.exc import PermissionDeniedError, EntityNotFoundError, InvalidOtpError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
    from Projeto_xirico.seguranca import Auditoria, Autenticacao
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.DTOs.operator_DTOs import ReactivateOperatorDTO

logger= logging.getLogger(__name__)


class ReactivateOperatorByEmail:
    def __init__(
        self, 
        message_box: messageBoxRepository,
        repo: OperatorRepository,
        profile: Profile,
        audit: Auditoria,
        auth: Autenticacao
        ) :
        self._message_box= message_box
        self._repo= repo
        self._profile= profile
        self._audit= audit
        self._auth = auth
        
        
    def execute(self,dados:ReactivateOperatorDTO ) -> Result[UpdateOutputDTO, BaseDomainError| OperatorError]:
        logger.debug('iniciando operacao de reactivacao de operador')
        otp= dados.otp
        email= dados.email
        warnings: list[BaseDomainError]= list()
        logger.debug('verificando permissao para reactivar operador')
        if not self._profile.ADM:
            logger.warning('permissao negada para reactivar o operador ')
            return Err(
                BaseDomainError.PERMISSION_DENIED_ERROR
            )

        try:
            logger.debug('verificando identidade do operador alvo em 2FA')
            self._auth.verificar_codigo(dados.otp)
        except InvalidOtpError:
            logger.warning('falha na verificacao otp errado')
            return Err(
                BaseDomainError.INCORRECT_OTP_ERROR
            )
        except InvalidTokenError:
            logger.warning('falha na verificacao otp invalido')
            return Err(
                BaseDomainError.INVALID_OTP_ERROR
            )

        try:
            logger.debug('reactivando operador')
            effect= self._repo.reactivate(email)
            logger.debug('recuperando os dados do operador')
            dados_= self._repo.search_email(email)
            operator_id= dados_.get('id')
            nome= dados_.get("nome")
            logger.info('operador: %s reactivado co sucesso', nome)
        except EntityNotFoundError:
            logger.warning('operador nao encontrado')
            return Err(OperatorError.OPERATOR_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical('falha ao conectar com o banco de dados',  exc_info=True)
            return Err(
                BaseDomainError.DB_CONECTION_ERROR
            )
        except DatabaseError:
            logger.error('erro inesperado com o banco de dados', exc_info=True)
            return Err(
                BaseDomainError.DB_ERROR
            )

        #registra um log de auditoria da operacao
        try:
            logger.debug('auditando a operacao de reactivacao')
            self._audit.auditar(
                operador= self._profile.id,
                operacao="reactivate operator",
                detalhes= f"reactivou o operador de email {email}")
        except Exception:
            logger.warning('falha inesperada ao auditar operacao', exc_info=True)
            warnings.append(BaseDomainError.AUDIT_FAILED)

        #enfileira um email para notificar o operador reactivado
        try:
            logger.debug('enfileirando email de notificacao')
            self._message_box.add_(
            dados={
                "to": email,
                "name":nome,
                "type": 'reactivate',
                "channel": 'email'
                }
            )  
        except DatabaseError:
            logger.warning(
                'falha inesperada ao enfileirar email', exc_info= True
                )
            warnings.append(
                BaseDomainError.MESSAGE_BOX_FAILLED
            )

        logger.debug('retorndo os resultados')
        return Ok(
            UpdateOutputDTO(
                warnings=warnings,
                effect= effect,
                old_data='active: False',
                new_data='active: True',
                updated_id= operator_id
            )
        )
        