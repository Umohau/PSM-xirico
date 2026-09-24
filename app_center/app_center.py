import os
import logging
from  dotenv import load_dotenv
from pathlib import Path
from Projeto_xirico.logger_config import setup_logging
from Projeto_xirico.app_setup import InitialSetUp
from Projeto_xirico.infra import InfraAuditoria, InfraData, InfraGerador,Conector
from Projeto_xirico.seguranca import Auditoria, GestorDeSessao, Autenticacao
from Projeto_xirico.profile import Profile
from Projeto_xirico.app_center.orders_app import OrderApp
from Projeto_xirico.app_center.catalog_app import CatalogApp
from Projeto_xirico.app_center.client_app import ClientApp
from Projeto_xirico.app_center.operator_app import OperatorApp
from Projeto_xirico.app_center.repository_center import RepositoryCenter
from Projeto_xirico.app_center.logging_app import SessionApp

logger= logging.getLogger(__name__)
#carrega o env com as configuracoes do app
BASE= Path(os.path.dirname(__file__))
env= BASE.parent/'config.env'
if not env.exists():
    raise FileExistsError('arwuivo env nao encontrado')
load_dotenv(env)

#inicalaza as infra_estruturas do app, tabelasa no banco,  pastas de arquivos
class InitInfra:
    def __init__(self, conector):
        self.infra_data= InfraData(conector= conector)
        self.infra_gerador= InfraGerador()
        self.infra_audit= InfraAuditoria()

log_config= setup_logging()# configura o logger raiz
CONECTION_STRING= os.getenv('DB_CONECTION_STRING')
CONECTOR=Conector(CONECTION_STRING)
infra= InitInfra(conector=CONECTOR) #inicializa o banco de dados
AUDITORIA= Auditoria()
AUTTENTICAO= Autenticacao()
SESSAO=GestorDeSessao(autenticador= AUTTENTICAO)
REPOSITORIES=RepositoryCenter(CONECTOR)



class SessionCenter:
    def __init__(self):
        self.session= SessionApp(
            session_menager= SESSAO,
            auth=AUTTENTICAO,
            audit=AUDITORIA,
            operator_repo= REPOSITORIES.operator_repository
        )

        self.initial_setup= InitialSetUp(
                    repo= REPOSITORIES.operator_repository,
                    audit= AUDITORIA,
                    auth=AUTTENTICAO
                )

        self.need_setup= not self.initial_setup.check_setup_status()


class AppCenter:
    def __init__(self, sessao):
        self.REPOSITORIES=REPOSITORIES


        PROFILE= Profile(
            sessao= sessao,
            repo_operador=self.REPOSITORIES.operator_repository,
            autenticador= AUTTENTICAO,
            auditoria=AUDITORIA)

        self.operator= OperatorApp(
            operator_repo= self.REPOSITORIES.operator_repository,
            auditoria= AUDITORIA,
            orders_repo= self.REPOSITORIES.orders_repository,
            shipments_repo= self.REPOSITORIES.shipments_repository,
            message_box= self.REPOSITORIES.message_box_repository,
            profile= PROFILE,
            auth= AUTTENTICAO
        )

        self.client= ClientApp(
            client_repo= self.REPOSITORIES.clients_repository,
            order_repo= self.REPOSITORIES.orders_repository,
            shipment_repo=self.REPOSITORIES.shipments_repository,
            audit= AUDITORIA,
            profile= PROFILE
        )

        self.orders= OrderApp(
            order_repo= self.REPOSITORIES.orders_repository,
            shipment_repo= self.REPOSITORIES.shipments_repository,
            profile= PROFILE,
            message_box= self.REPOSITORIES.message_box_repository,
            auth= Autenticacao,
            audit= AUDITORIA,
            operator_repo= self.REPOSITORIES.operator_repository
        )

        self.catalog= CatalogApp(
            birds_repo= self.REPOSITORIES.birds_repository,
            audit= AUDITORIA,
            profile= PROFILE
        )
