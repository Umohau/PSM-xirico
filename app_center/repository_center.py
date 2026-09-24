from Projeto_xirico.repositories.birds_repository import BirdsRepository
from Projeto_xirico.repositories.cliente_repository import ClientsRepository
from Projeto_xirico.repositories.shipment_repository import ShipmentRepository
from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
from Projeto_xirico.repositories.operator_repository import OperatorRepository
from Projeto_xirico.repositories.orders_repository import OrdersRepository


class RepositoryCenter:
    def __init__(self, conector):
        self.orders_repository= OrdersRepository(conector= conector)

        self.shipments_repository= ShipmentRepository(conector= conector)

        self.clients_repository= ClientsRepository(conector= conector)

        self.message_box_repository= messageBoxRepository(conector= conector)

        self.operator_repository= OperatorRepository(conector= conector)

        self.birds_repository= BirdsRepository(conector= conector)
