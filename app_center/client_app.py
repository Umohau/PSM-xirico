from Projeto_xirico.use_cases.client_use_cases.client_update_address_by_id import ClientUpdateAdressById
from Projeto_xirico.use_cases.client_use_cases.client_update_domain_by_id import ClientUpdateDomainById
from Projeto_xirico.use_cases.client_use_cases.client_update_email import ClientUpdateEmail
from Projeto_xirico.use_cases.client_use_cases.client_update_name_by_id import ClientUpdateNameById
from Projeto_xirico.use_cases.client_use_cases.client_update_telephone_by_id import ClientUpdateTelephoneBYId
from Projeto_xirico.use_cases.client_use_cases.delete_client_by_id import DeleteClientById
from Projeto_xirico.use_cases.client_use_cases.list_client_orders import ListClientOrders
from Projeto_xirico.use_cases.client_use_cases.list_client_shipments import ListClientShipments
from Projeto_xirico.use_cases.client_use_cases.list_clients import ListClients
from Projeto_xirico.use_cases.client_use_cases.recovery_client import RecoveryClient
from Projeto_xirico.use_cases.client_use_cases.regist_new_client import RegistNEwClient
from Projeto_xirico.use_cases.client_use_cases.search_client_by_id import SearchClientById
from Projeto_xirico.use_cases.client_use_cases.search_client_by_name import SearchClietByName


class ClientApp:
    def __init__(self,
        client_repo,
        order_repo,
        shipment_repo,
        audit,
        profile
    ):
        
        self.regist_new_client= RegistNEwClient(
            repo=client_repo,
            audit= audit,
            profile= profile
        )

        
        self.recovery_client= RecoveryClient(
            repo=client_repo,
            profile= profile,
            audit= audit
        )


        self.search_client_by_id= SearchClientById(
            repo=client_repo,
            profile= profile
        )


        self.search_client_by_name= SearchClietByName(
            repo= client_repo,
            profile= profile
        )
        
        self.list_clients= ListClients(
            repo= client_repo,
            profile=profile
        )

        
        self.list_client_shipment= ListClientShipments(
            repo=shipment_repo
        )


        self.list_client_orders= ListClientOrders(
            repo=order_repo
        )

        
        self.delete_client_by_id= DeleteClientById(
            repo=client_repo,
            profile= profile,
            audit= audit
        )

        
        self.client_update_telephone_by_id= ClientUpdateTelephoneBYId(
            repo= client_repo,
            profile= profile,
            audit= audit
        )

        
        self.client_update_name_by_id= ClientUpdateNameById(
            repo= client_repo,
            profile= profile,
            audit= audit
        )

        
        self.client_update_domain_by_id= ClientUpdateDomainById(
            repo= client_repo,
            profile= profile,
            audit= audit
        )


        self.client_update_address_by_id= ClientUpdateAdressById(
            repo= client_repo,
            profile= profile,
            audit= audit
        )


        self.client_update_email= ClientUpdateEmail(
            repo=client_repo,
            profile= profile,
            audit=audit
        )