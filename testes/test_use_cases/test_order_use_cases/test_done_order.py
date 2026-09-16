import pytest
from datetime import datetime, timezone
from unittest.mock import PropertyMock
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.DTOs.shipment_DTO import RegistShipmentDTO
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.use_cases.orders_use_cases.done_order import DoneOrder
from Projeto_xirico.exc import EntityNotFoundError, InvalidOtpError

@pytest.fixture
def done_order(mock_repo, mock_profile, mock_audit):
    return DoneOrder(audit= mock_audit, profile= mock_profile, order= mock_repo, shipment= mock_repo)

@pytest.fixture
def dados(tmp_path):
    open(tmp_path/'teste.pdf', 'x')
    with open(tmp_path/'teste.pdf', 'rb') as arquivo:
        docs= arquivo.read()
        return RegistShipmentDTO(
            sent_at= datetime.now(timezone.utc).date(),
            order_id= 'ÓRD213',
            process_docs= docs
        )

def test_done_order_sucess(mock_repo, mock_audit, done_order, dados):
    res= done_order.execute(dados)
    mock_repo.get_order_oid.assert_called()
    mock_repo.insert.assert_called()
    mock_repo.update.assert_called()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, InsertOutputDTO)
    assert len(output.warnings) == 0


def test_done_order_pemission_denied(mock_profile, mock_repo, mock_audit, done_order, dados):
    type(mock_profile).ADM=PropertyMock(return_value= False)
    res= done_order.execute(dados)
    mock_repo.get_order_oid.assert_called()
    mock_repo.insert.assert_not_called()
    mock_repo.update.assert_not_called()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value


def test_done_order_entity_not_found(mock_repo, mock_audit, done_order, dados):
    mock_repo.get_order_oid.side_effect= EntityNotFoundError
    res= done_order.execute(dados)
    mock_repo.get_order_oid.assert_called()
    mock_repo.insert.assert_not_called()
    mock_repo.update.assert_not_called()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value


def test_done_order_shipment_insert_error(mock_repo, mock_audit, done_order, dados):
    mock_repo.insert.side_effect= OperationalError('error', (9), 'main')
    res= done_order.execute(dados)
    mock_repo.get_order_oid.assert_called()
    mock_repo.insert.assert_called()
    mock_repo.update.assert_not_called()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_done_order_update_status_order_failled(mock_repo, mock_audit, done_order, dados):
    mock_repo.update.side_effect= OperationalError('error', (9), 'main')
    res= done_order.execute(dados)
    mock_repo.get_order_oid.assert_called()
    mock_repo.insert.assert_called()
    mock_repo.update.assert_called()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.OPEERATION_FAILLED.value


def test_done_order_orphan_data_error(mock_repo, mock_audit, done_order, dados):
    mock_repo.update.side_effect= OperationalError('error', (9), 'main')
    mock_repo.delete.side_effect= OperationalError('error', (9), 'main')
    res= done_order.execute(dados)
    mock_repo.get_order_oid.assert_called()
    mock_repo.insert.assert_called()
    mock_repo.update.assert_called()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, InsertOutputDTO)
    assert BaseDomainError.ORPHAN_DATA_ERROR.value in output.warnings


def test_done_order_audit_failled(mock_repo, mock_audit, done_order, dados):
    mock_audit.auditar.side_effect= FileNotFoundError
    res= done_order.execute(dados)
    mock_repo.get_order_oid.assert_called()
    mock_repo.insert.assert_called()
    mock_repo.update.assert_called()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, InsertOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings