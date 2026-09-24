from Projeto_xirico.use_cases.orders_use_cases.search_shipmants import SearchShipmentByOrderId, SearchShipmentsByEpoc
from Projeto_xirico.use_cases.orders_use_cases.search_order import SearcbOrdersByOrderId
from Projeto_xirico.use_cases.orders_use_cases.update_quantity_bird_off_order import UpdateQuantityBirdOfOrder
from Projeto_xirico.use_cases.orders_use_cases.change_order_bird import ChangeOrderBird
from  Projeto_xirico.use_cases.orders_use_cases.add_new_order import AddNewOrder
from Projeto_xirico.use_cases.orders_use_cases.cancel_order import CancelOrder
from Projeto_xirico.use_cases.orders_use_cases.change_order_client import ChangeOrderClient
from Projeto_xirico.use_cases.orders_use_cases.change_order_maneger import  ChangeOrderMenager
from Projeto_xirico.use_cases.orders_use_cases.delete_order import DeleteOrder
from Projeto_xirico.use_cases.orders_use_cases.done_order import DoneOrder

class OrderApp:
    def __init__(self,
        order_repo,
        shipment_repo,
        profile,
        message_box,
        auth,
        audit,
        operator_repo):
        self.add_new_order= AddNewOrder(
            repo= order_repo,
            profile= profile,
            audit=audit
        )

        
        self.delete_order= DeleteOrder(
            repo= order_repo,
            profile= profile,
            audit= audit
        )


        self.cancel_order= CancelOrder(
            repo= order_repo,
            profile= profile,
            audit= audit
        )


        self.done_order= DoneOrder(
            order= order_repo,
            shipment= shipment_repo,
            profile=profile,
            audit= audit
        )


        self.change_order_menager= ChangeOrderMenager(
            repo= order_repo,
            profile= profile,
            audit=audit,
            message_box= message_box,
            operator= operator_repo, 
            auth= auth
        )


        self.change_order_client= ChangeOrderClient(
            repo= order_repo,
            profile= profile,
            audit= audit
        )


        self.change_order_bird=  ChangeOrderBird(
            repo= order_repo,
            profile= profile,
            audit= audit
        )


        self.search_order_by_id= SearcbOrdersByOrderId(
            repo= order_repo
        )


        self.order_update_bird_quantity_by_id= UpdateQuantityBirdOfOrder(
            repo= order_repo,
            profile= profile,
            audit= audit
        )


        self.search_shipment_by_epoc= SearchShipmentsByEpoc(
            repo= shipment_repo
        )

        self.search_shipment_by_id= SearchShipmentByOrderId(
            repo= shipment_repo
        )