import pytest
from datetime import datetime, timezone
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.DTOs.orders_DTOS import OrderGetResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.use_cases.orders_use_cases.search_order import SearcbOrdersByOrderId
from Projeto_xirico.exc import EntityNotFoundError

@pytest.fixture
def search_order_by_id(mock_repo):
    return SearcbOrdersByOrderId(repo= mock_repo)


dados={
    'cliente_id':1,
    'gestor_id':4,
    'ave_id':4,
    'quantidade':566,
    'registado_at': datetime.now(timezone.utc).date(),
    'order_id': 'ORD13',
    'estado':'pendente',
    'enviado_at':None
}


def test_search_order_sucess(search_order_by_id, mock_repo):
    mock_repo.search_oid.return_value= dados
    res= search_order_by_id.execute('ORD123')
    mock_repo.search_oid.assert_called()
    assert is_ok(res)
    assert isinstance(res.unwrap(), OrderGetResponseDTO)


def test_search_order__order_not_found(search_order_by_id, mock_repo):
    mock_repo.search_oid.side_effect= EntityNotFoundError
    res= search_order_by_id.execute('ORD123')
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value


def test_search_orders_db_error(search_order_by_id, mock_repo):
    mock_repo.search_oid.side_effect= DatabaseError('error', (9), 'main')
    res= search_order_by_id.execute('ORD123')
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value



def test_search_orders_db_conection_error(search_order_by_id, mock_repo):
    mock_repo.search_oid.side_effect= OperationalError('error', (9), 'main')
    res= search_order_by_id.execute('ORD123')
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value