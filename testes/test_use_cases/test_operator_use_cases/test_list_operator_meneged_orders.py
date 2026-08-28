import pytest
from result import is_ok, is_err
from datetime import datetime

from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import OrderError, BaseDomainError
from Projeto_xirico.DTOs.orders_DTOS import OrderGetResponseDTO
from Projeto_xirico.use_cases.operator_use_cases.list_operator_maneged_orders import ListOperatorMenagedOrders


@pytest.fixture
def list_operator_maneged_orders(mock_repo):
    return ListOperatorMenagedOrders(mock_repo)

@pytest.fixture
def dados(tmp_path):
    return{
        'order_id': 'ORD123',
        'gestor_id': 1,
        'cliente_id': 2,
        'registado_at': datetime.now().date(),
        'enviado_at':None,
        'bird_id':2,
        "quantidade":200,
        'status': 'Pending'

    }
def test_list_operator_menaged_orders_sucess(mock_repo, list_operator_maneged_orders, dados):
    id=1
    mock_repo.get_order_gid.return_value= [dados]
    res= list_operator_maneged_orders .execute(operator_id= id)
    output= res.unwrap()
    mock_repo.get_order_gid.assert_called_once()
    assert is_ok(res)
    assert isinstance(output, list)
    assert isinstance(output[0],OrderGetResponseDTO )


def test_list_operator_menaged_orders_entity_not_found_error(
    mock_repo,
    list_operator_maneged_orders,
    dados
):
    id=1
    mock_repo.get_order_gid.side_effect= EntityNotFoundError
    res= list_operator_maneged_orders.execute(operator_id= id)
    output= res.unwrap_err()
    mock_repo.get_order_gid.assert_called_once()
    assert is_err(res)
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value



def test_list_operator_menaged_orders_db_conection_error(
    mock_repo,
    list_operator_maneged_orders,
):
    id=1
    mock_repo.get_order_gid.side_effect= OperationalError('erro', (9), 'main')
    res= list_operator_maneged_orders.execute(operator_id= id)
    output= res.unwrap_err()
    mock_repo.get_order_gid.assert_called_once()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value



def test_list_operator_menaged_orders_db_error(
    mock_repo,
    list_operator_maneged_orders
):
    id=1
    mock_repo.get_order_gid.side_effect= DatabaseError('erro', (9), 'main')
    res= list_operator_maneged_orders.execute(operator_id= id)
    output= res.unwrap_err()
    mock_repo.get_order_gid.assert_called_once()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value