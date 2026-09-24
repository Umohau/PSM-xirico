from Projeto_xirico.repositories.operator_repository import OperatorRepository
from Projeto_xirico.seguranca import Autenticacao, Auditoria
from Projeto_xirico.DTOs.operator_DTOs import RegistOperatorDTO


class InitialSetUp:

    def __init__(
        self,
        repo: OperatorRepository,
        audit: Auditoria,
        auth: Autenticacao
    ):
        self.repo = repo
        self.auth = auth
        self.audit = audit

    def check_setup_status(self) -> bool:
        """
        Verifica se o banco já possui operadores.

        Returns:
            True: já existe pelo menos um operador.
            False: não existe nenhum operador.
        """

        return self.repo.total_records > 0

    def collect_data(self, dados: RegistOperatorDTO) -> dict:
        senha_hash = self.auth.hashear(dados.password)

        return {
            "nome": dados.name,
            "identificacao": dados.BI,
            "telefone": dados.telephone,
            "email": dados.email,
            "endereco": dados.adress,
            "senha": senha_hash,
            "ADM": True,
            "ativo": True,
        }

    def execute(self, dados: RegistOperatorDTO):
        dados_ = self.collect_data(dados)
        operator_id = self.repo.insert(dados_)

        return operator_id