import pytest
from unittest.mock import PropertyMock
from datetime import datetime, timezone
from unittest.mock import PropertyMock
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.use_cases.orders_use_cases.cancel_order import CancelOrder
from Projeto_xirico.exc import EntityNotFoundError, InvalidOtpError


@pytest.fixture
def  cancel_order(mock_repo, mock_profile, mock_audit):
    return CancelOrder(repo= mock_repo, profile= mock_profile, audit= mock_audit)


def test_cancel_order_sucess(mock_repo, mock_profile, mock_audit, cancel_order):
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value={'gestor_id':4, 'estado': 'pendente'}
    res= cancel_order.execute('ORD123')
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) == 0


def test_cancel_order_audit_failled(mock_repo, mock_audit, mock_profile, cancel_order):
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value={'gestor_id':4, 'estado': 'pendente'}
    res= cancel_order.execute('ORD123')
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings



def test_cancel_order_order_not_found(mock_repo, mock_audit, cancel_order):
    mock_repo.get_order_oid.side_effect= EntityNotFoundError
    res= cancel_order.execute('ORD123')
    assert is_err(res)
    mock_audit.auditar.assert_not_called()
    mock_repo.update.assert_not_called()
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value



def test_cancel_order_permission_denied(mock_repo, mock_audit, mock_profile, cancel_order):
    type(mock_profile).ADM= PropertyMock(return_value=False)
    mock_repo.get_order_oid.return_value={'gestor_id':4, 'estado': 'pendente'}
    res= cancel_order.execute('ORD123')
    mock_audit.auditar.assert_not_called()
    mock_repo.update.assert_not_called()
    mock_repo.get_order_oid.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert BaseDomainError.PERMISSION_DENIED_ERROR.value == output.value


def test_cancel_order_db_conection_error(mock_repo, mock_audit, mock_profile, cancel_order):
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_repo.get_order_oid.return_value={'gestor_id':4, 'estado': 'pendente'}
    mock_repo.update.side_effect= OperationalError('error', (9), 'main')
    res= cancel_order.execute('ORD123')
    mock_audit.auditar.assert_not_called()
    mock_repo.update.assert_called()
    mock_repo.get_order_oid.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert BaseDomainError.DB_CONECTION_ERROR.value == output.value



def test_cancel_order_db_error(mock_repo, mock_audit, mock_profile, cancel_order):
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_repo.get_order_oid.return_value={'gestor_id':4, 'estado': 'pendente'}
    mock_repo.update.side_effect= DatabaseError('error', (9), 'main')
    res= cancel_order.execute('ORD123')
    mock_audit.auditar.assert_not_called()
    mock_repo.update.assert_called()
    mock_repo.get_order_oid.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert BaseDomainError.DB_ERROR.value == output.value