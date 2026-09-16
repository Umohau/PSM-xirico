import pytest
from datetime import datetime, timezone
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.DTOs.orders_DTOS import OrderRegistDTO
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.use_cases.orders_use_cases.delete_order import DeleteOrder


@pytest.fixture
def delete_order(mock_repo, mock_profile, mock_audit):
    return DeleteOrder(profile= mock_profile, audit= mock_audit, repo= mock_repo)


def test_delete_order_sucess(mock_repo, mock_audit, delete_order):
    mock_repo.delete.return_value=1
    res= delete_order.execute(1)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output=res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings)== 0


def test_delete_order_not_found(mock_repo, mock_audit, delete_order):
    mock_repo.get_order_oid.side_effect= EntityNotFoundError
    res= delete_order.execute(1)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value


def test_delete_order_db_connection_error(mock_repo, mock_audit, delete_order):
    mock_repo.delete.side_effect= OperationalError('error', (9), 'main')
    res= delete_order.execute(1)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_delete_order_db_error(mock_repo, mock_audit, delete_order):
    mock_repo.delete.side_effect= DatabaseError('error', (9), 'main')
    res= delete_order.execute(1)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_delete_order_audit_failled(mock_audit, mock_repo, delete_order):
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.delete.return_value=1
    res= delete_order.execute(1)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output=res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
