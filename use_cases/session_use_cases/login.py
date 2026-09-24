import os
from pathlib import Path
import time
from dotenv import load_dotenv
from result import Result, Err, Ok, is_err, is_ok
from sqlalchemy.exc import DatabaseError
from Projeto_xirico.DTOs.session_DTOs import LoginOutput
from Projeto_xirico.DTOs.session_DTOs import EnterUserDataDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, SessionError
from Projeto_xirico.repositories.operator_repository import OperatorRepository
from Projeto_xirico.seguranca import Autenticacao, Auditoria, GestorDeSessao
from Projeto_xirico.exc import EntityNotFoundError

#carrega o env com as configuracoes do app
BASE= Path(os.path.dirname(__file__))
env= BASE.parent.parent/'config.env'
if not env.exists():
    raise FileNotFoundError('arquivo env nao encontrado')
load_dotenv(env)

LOGIN_LOCKOUT_TIME_SECOND= int(os.getenv('LOGIN_LOCKOUT_TIME_SECOND', 24*60*60))


class LogIN:
    def __init__(self,session_menager:GestorDeSessao, auth: Autenticacao, audit:Auditoria, repo: OperatorRepository):
        self._repo= repo
        self._auth= auth
        self._audit= audit
        self._session_menager= session_menager
        self._warnings:list[BaseDomainError]= list()
        self.__count=0
        self.__blocked_until=0

    def check_blocked_status(self):
        if self.__count == 10:
            if self.__blocked_until >= time.time():
                return Err(SessionError.LOGIN_BLOCKED_ERROR)
            self.__blocked_until=0
            self.__count=0
        return Ok(True)
    

    def get_operator_data(self, email):
        try:
            operator= self._repo.search_email(email= email)
        except EntityNotFoundError:
            self.__count+=1
            if self.__count >= 10:
                self.__blocked_until= time.time() + LOGIN_LOCKOUT_TIME_SECOND
            return Err(SessionError.CREDENTIALS_ERROR)
        except DatabaseError:
            return Err(BaseDomainError.DB_ERROR)

        return Ok(operator)


    def get_operator_password(self, email):
        try:
            operator_password= self._repo.get_password(email= email)
        except DatabaseError:
            return Err(BaseDomainError.DB_ERROR)
        if operator_password is None:
            self.__count+=1
            if self.__count >= 10:
                self.__blocked_until= time.time() + LOGIN_LOCKOUT_TIME_SECOND
            return Err(SessionError.CREDENTIALS_ERROR)
        return Ok(operator_password)

    
    def execute_log_in(self, logging_data: EnterUserDataDTO) -> Result[LoginOutput, BaseDomainError| SessionError]:
        email= logging_data.user_email
        password= logging_data.user_password

        block_status= self.check_blocked_status()
        if is_err(block_status):
            return block_status
        

       #recupera os dados do usuario no banco de dados
       #para serem carregados no token
        operator_= self.get_operator_data(email= email)
        if is_err(operator_):
            return operator_
        operator= operator_.unwrap()
        operator_id= operator['id']
        operator_ADM= operator['ADM']
        operator_name= operator['nome']
        
            

        #recupera a senha do operador no banco de dados
        operator_password_= self.get_operator_password(email= email)
        if is_err(operator_password_):
            return operator_password_
        operator_password= operator_password_.unwrap()

        #verifica a compatibilidade entre as senhas
        acess=self._auth.verificar_senha(senha= password, senha_armazenada= operator_password)
        if not acess:
            self.__count+=1
            if self.__count >= 10:
                self.__blocked_until= time.time() + LOGIN_LOCKOUT_TIME_SECOND
            return Err(SessionError.CREDENTIALS_ERROR)
            
        #gera um token de acesso
        token= self._auth.gerar_token(
            {
                'id':operator_id,
                'ADM':operator_ADM,
                'name': operator_name
            }
        )

        #registra a operacao de login
        try:
            self._audit.auditar(
                operator_id= operator_id,
                operacao='login',
                detalhes='iniciou sessao'
            )
        except Exception:
            self._warnings.append(BaseDomainError.AUDIT_FAILED)

        #retorna um objeto de sessao com a sessao iniciada
        self.__blocked_until=0
        self.__count=0

        #inicia sessao no gestor de sessao
        self._session_menager.iniciar_sessao(token= token)

        return Ok(
            LoginOutput(
                session=self._session_menager,
                warnings= self._warnings
            )
        )
