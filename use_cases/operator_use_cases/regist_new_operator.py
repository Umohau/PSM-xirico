from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from result import Result, Ok, Err
from sqlalchemy.exc import OperationalError,  DatabaseError
from jwt.exceptions import InvalidTokenError

from Projeto_xirico.exc import PermissionDeniedError, CredentialsError, DuplicateError, InvalidOtpError
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.seguranca import Autententicacao,  Auditoria
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
    from Projeto_xirico.DTOs.operator_DTOs import RegistOperatorDTO
    
logger=logging.getLogger(__name__)

        
class RegistNewOperator:
    def __init__(
        self,
        repo: OperatorRepository,
        auth:Autententicacao,
        message_box: messageBoxRepository,
        profile: Profile,
        audit: Auditoria
        ):
        self._repo= repo
        self._auth= auth
        self._message_box= message_box
        self._profile= profile
        self._audit= audit
        
        
    def execute(
        self,
        dados:RegistOperatorDTO
        ) -> Result[InsertOutputDTO, BaseDomainError | OperatorError]:
        """
           
        Registers a new operator in the system.
    
        This method performs the complete registration workflow:
        1. Verifies that the current operator has ADMIN privileges.
        2. Ensures that the provided operator data (email, username, etc.) are unique.
        3. Validates the one‑time password (OTP) sent to the new operator's email.
        4. Persists the new operator record in the repository.
        5. Logs the operation in the audit trail.
        6. Sends a welcome email to the new operator (non‑critical; failures are logged).
    
        Args:
            dados (OperatorRegist): Pydantic model containing the new operator's data
                (e.g., name, email, username, role, etc.).
            otp (str): 8‑digit code previously emailed to the new operator for identity
                verification.
    
        Returns:
            int: The unique identifier (ID) assigned to the newly registered operator.
    
        Raises:
            PermissionDeniedError: If the current operator is not an ADMIN.
            DuplicateError: If any of the provided data (email/username) already exists.
            InvalidOtpError: If the OTP does not match the expected value.
            ExpiredOtpError: If the OTP has expired (time window exceeded).
            AttemptsExcededError: If the OTP has been entered incorrectly more than
                the allowed number of times.
    
        Notes:
            - The OTP verification and uniqueness checks are delegated to the `auth`
              and `repo` dependencies, which raise the appropriate exceptions.
            - Email notification failures are caught and logged as warnings; they do
              not block the registration process.
            - All operations are audited for traceability.
    
        """
        logger.debug('iniciando cadastro do opeprator')
        Warnings: list[BaseDomainError| OperatorError]= list()
        logger.debug('verificando permicao')
        if not self._profile.ADM:
            logger.error('permicao negada')
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)
        try:
            self._repo.check_unique(dados.model_dump()) #verifica a unicidade dos dados
        except DuplicateError as e:
            campos= ['email', 'telefone', 'BI']
            for campo in campos:
                key= f'OPERATOR_DUPLICATE_{campo.upper()}_ERROR'
                if campo in str(e):
                    chave: OperatorError= getattr(OperatorError, key)
                    return Err(chave)
        try:
            logger.debug('verificando a identidade em 2FA')
            self._auth.verificar_otp(dados.otp) #verifica o codigo otp
        except InvalidTokenError:
            logger.debug('codigo otp invalido')
            return Err(BaseDomainError.INVALID_OTP_ERROR)
        except InvalidOtpError:
            logger.debug('codigo otp incorecto')
            return Err(BaseDomainError.INCORRECT_OTP_ERROR)

        try:
            logger.debug(('persistindo os dados'))
            id_gerado= self._repo.insert(dados.model_dump()) #persiste os dados no repositorio
            logger.info(f'operador {dados.name}, registrado com id {id_gerado}')
        except OperationalError:
            logger.critical('erro ao conecta com o banco de dados', exc_info=True)
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error('erro inesperado no banco de dados', exc_info= True)
            return Err(BaseDomainError.DB_ERROR)

        try:
            logger.debug('auditando a operacao  de registro')
            self._audit.auditar(
                operador= self._profile.id,
                operacao= "regist new operator",
                detalhes= f"registou  um operador com o id {id_gerado}")
            logger.debug('operacao auditada co sucesso')
        except DatabaseError:
            logger.warning('falha ao auditar operacao de registro', exc_info=True)
            Warnings.append(BaseDomainError.AUDIT_FAILED)

        
        #adiciona uma mensagem de boas vindas na caixa para posterior envio
        try:
            logger.debug('enfileirando email de boas vindas')
            self._message_box.add_(
                dados={
                    "to":dados.email,
                    "type":'welcome',
                    "name": dados.name,
                    "channel": 'email'
                } )
            logger.debug('email adicionado a fila com sucesso')
        except DatabaseError:
            logger.warning('falha ao enfileirar email de boas vindas', exc_info=True)
            Warnings.append(BaseDomainError.MESSAGE_BOX_FAILLED)
        logger.debug('retorndo o resultado da operacao')
        return Ok(
            InsertOutputDTO(
            warnings= Warnings,
            genereted_id= id_gerado
        ))
        