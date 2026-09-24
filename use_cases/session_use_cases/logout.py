from typing import TYPE_CHECKING
from result import Result, Ok, Err
from Projeto_xirico.domain_exceptions import SessionError
from Projeto_xirico.seguranca import GestorDeSessao
if TYPE_CHECKING:
    from Projeto_xirico.seguranca import GestorDeSessao

class LogOut:
    def __init__(self, session_menager:GestorDeSessao):
        self.session= session_menager

    def check_session_status(self) -> bool:
        """
        verifica se tem sessao iniciada no gestor de sessao

        Returns:
            True: se gestor de sessao tiver sessao iniciada
            False: se gestor de sessao nao tiver sessao iniciada
        """
        if self.session.token == None:
            return False
        return True


    def execute(self):
       if not self.check_session_status():
           return Err(SessionError.UNTRACED_SESSION_ERROR)
       self.session.terminar_sessao()
       return Ok(True)

