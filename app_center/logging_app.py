from Projeto_xirico.use_cases.session_use_cases.login import LogIN
from Projeto_xirico.use_cases.session_use_cases.logout import LogOut

class SessionApp:
    def __init__(self, session_menager, auth, audit, operator_repo):
        self.login= LogIN(
            session_menager= session_menager,
            auth= auth,
            audit= audit,
            repo= operator_repo
        )


        self.logout=LogOut( session_menager= session_menager)