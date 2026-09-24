from Projeto_xirico.use_cases.operator_use_cases import regist_new_operator, disable_operator_by_id
from Projeto_xirico.use_cases.operator_use_cases import demote_operator, promote_operator
from Projeto_xirico.use_cases.operator_use_cases import reactivate_operator_by_email, get_inactive_operators
from Projeto_xirico.use_cases.operator_use_cases import list_operator_shipments, list_operator_maneged_orders
from Projeto_xirico.use_cases.operator_use_cases import list_active_operators


class OperatorApp:
    def __init__(self,
        operator_repo,
        auditoria,
        orders_repo,
        shipments_repo,
        message_box,
        profile,
        auth
    ):

        self.list_active_operators= list_active_operators.ListActiveOperators(
            repo= operator_repo, profile= profile,
            audit= auditoria
        )


        self.list_operator_menaged_orders= list_operator_maneged_orders.ListOperatorMenagedOrders(
            repo= orders_repo
        )


        self.list_operator_shipmetns= list_operator_shipments.ListOperatorShipments(
            repo= shipments_repo
        )


        self.get_inactive_operators= get_inactive_operators.GetInactiveOperators(
            repo= operator_repo,
            profile= profile
        )


        self.reactivate_operator_by_email= reactivate_operator_by_email.ReactivateOperatorByEmail(
            repo= operator_repo,
            message_box= message_box,
            profile= profile,
            audit= auditoria,
            auth= auth
        )



        self.regist_new_operator= regist_new_operator.RegistNewOperator(
           repo=operator_repo,
           auth= auth,
           message_box= message_box,
           profile= profile,
           audit=auditoria
       )


        self.disable_operator_by_id= disable_operator_by_id.DisableOperatorByID(
           repo= operator_repo,
           message_box= message_box,
           profile= profile,
           audit= auditoria
       )


        self.promote_operator= promote_operator.PromoteOperator(
           repo= operator_repo,
           message_box= message_box,
           profile= profile,
           audit= auditoria
       )


        self.demote_operator= demote_operator.DemoteOperator(
           repo= operator_repo,
           profile= profile,
           audit=auditoria,
           message_box= message_box
        )
