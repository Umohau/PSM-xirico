import pytest
from datetime import datetime, timezone
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.DTOs.orders_DTOS import OrderRegistDTO
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError
from Projeto_xirico.use_cases.orders_use_cases.add_new_order import AddNewOrder


dados= OrderRegistDTO(
    date_of_regist= datetime.now(timezone.utc).date(),
    menager_id=1,
    client_id=2,
    quantity=200,
    bird= 2
)

@pytest.fixture
def add_new_order(mock_repo, mock_profile, mock_audit):
    return AddNewOrder(profile= mock_profile, audit= mock_audit, repo= mock_repo)


def test_add_new_order_sucess(mock_repo, mock_audit, add_new_order):
    mock_repo.insert.return_value= 'ORD123'
    res= add_new_order.execute(dados)
    mock_repo.insert.assert_called_once()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, InsertOutputDTO)
    assert len(output.warnings) == 0


def test_add_new_order_invalid_input(mock_repo, mock_audit, add_new_order):
    mock_repo.insert.side_effect= IntegrityError('error', (9), 'main')
    res= add_new_order.execute(dados)
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.INVALID_INPUT_DATA.value


def test_add_new_order_db_conection_error(mock_repo, mock_audit, add_new_order):
    mock_repo.insert.side_effect= OperationalError('erro', (9), 'main')
    res= add_new_order.execute(dados)
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value



def test_add_new_order_db_error(mock_repo, mock_audit, add_new_order):
    mock_repo.insert.side_effect= DatabaseError('erro', (9), 'main')
    res= add_new_order.execute(dados)
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value



def test_add_new_order_audit_failled(mock_repo, mock_audit, add_new_order):
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.insert.return_value= 'ORD123'
    res= add_new_order.execute(dados)
    mock_repo.insert.assert_called_once()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, InsertOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
