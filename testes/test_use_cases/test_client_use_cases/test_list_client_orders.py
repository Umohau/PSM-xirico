import pytest
from datetime import datetime
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError,DatabaseError
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.DTOs.orders_DTOS import OrderGetResponseDTO
from Projeto_xirico.use_cases.client_use_cases.list_client_orders import ListClientOrders


dados=[{
        'order_id': 'ORD123',
        'gestor_id': 1,
        'cliente_id': 2,
        'registado_at': datetime.now().date(),
        'enviado_at':None,
        'bird_id':2,
        "quantidade":200,
        'status': 'Pending'

    }]


@pytest.fixture
def list_client_orders(mock_repo):
    return ListClientOrders(mock_repo)


def test_list_client_orders_sucess(mock_repo, list_client_orders):
    mock_repo.get_orders_cid.return_value= dados
    res= list_client_orders.execute(1)
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, list)
    assert isinstance(output[0], OrderGetResponseDTO)


def test_list_client_orders_orders_not_found(mock_repo, list_client_orders):
    mock_repo.get_orders_cid.side_effect= EntityNotFoundError
    res= list_client_orders.execute(1)
    mock_repo.get_orders_cid.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value



def test_list_client_orders_db_conection_error(mock_repo, list_client_orders):
    mock_repo.get_orders_cid.side_effect= OperationalError('eror', (9), 'main')
    res= list_client_orders.execute(1)
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_list_client_orders_db_error(mock_repo, list_client_orders):
    mock_repo.get_orders_cid.side_effect= DatabaseError('eror', (9), 'main')
    res= list_client_orders.execute(1)
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value
