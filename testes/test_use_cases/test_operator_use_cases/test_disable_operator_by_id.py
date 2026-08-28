import pytest
from unittest.mock import PropertyMock
from result import is_ok, is_err
from sqlalchemy.exc import DatabaseError, OperationalError

from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.exc import PermissionDeniedError, EntityNotFoundError
from Projeto_xirico.use_cases.operator_use_cases.disable_operator_by_id import DisableOperatorByID


@pytest.fixture
def disable_operator_by_id(mock_repo, mock_profile, mock_audit, mock_message_box):
    return DisableOperatorByID(
        repo= mock_repo,
        message_box= mock_message_box,
        profile= mock_profile,
        audit= mock_audit
    )


def test_disable_operator_by_id_sucess(
    disable_operator_by_id,
    mock_repo,
    mock_message_box,
    mock_audit
):
    id=1
    res= disable_operator_by_id.execute(id)
    output= res.unwrap()
    mock_repo.search_id.assert_called_once_with(id)
    mock_repo.delete.assert_called_once_with(id)
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) ==0


def test_disable_operator_by_id_permission_denied(
    disable_operator_by_id,
    mock_repo,
    mock_message_box,
    mock_audit,
    mock_profile
):
    id=1
    type(mock_profile).ADM= PropertyMock(return_value=False)
    
    res= disable_operator_by_id.execute(id)
    output= res.unwrap_err()
    mock_repo.search_id.assert_not_called()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value


def test_disable_operator_by_id_entity_not_found(
    disable_operator_by_id,
    mock_repo,
    mock_message_box,
    mock_audit
):
    id=1
    mock_repo.search_id.side_effect= EntityNotFoundError
    res= disable_operator_by_id.execute(id)
    output= res.unwrap_err()
    mock_repo.search_id.assert_called_once()
    mock_repo.delete.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, OperatorError)
    assert output.value == OperatorError.OPERATOR_NOT_FOUND_ERROR.value


def test_disable_operator_by_id_db_conection_error(
    disable_operator_by_id,
    mock_repo,
    mock_message_box,
    mock_audit
):
    id=1
    mock_repo.delete.side_effect= OperationalError('erro', (9), "main")
    res= disable_operator_by_id.execute(id)
    output= res.unwrap_err()
    mock_repo.search_id.assert_called_once()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_disable_operator_by_id_audit_failled(
    disable_operator_by_id,
    mock_repo,
    mock_message_box,
    mock_audit 
):
    id=1
    mock_audit.auditar.side_effect= FileNotFoundError
    res= disable_operator_by_id.execute(id)
    output= res.unwrap()
    mock_repo.search_id.assert_called_once()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    mock_message_box.add_.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings)==1
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings


def test_disable_operator_by_id_message_box_failled(
    disable_operator_by_id,
    mock_repo,
    mock_message_box,
    mock_audit 
):
    id=1
    mock_message_box.add_.side_effect= DatabaseError('erro', (4), 'main')
    res= disable_operator_by_id.execute(id)
    output= res.unwrap()
    mock_repo.search_id.assert_called_once()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    mock_message_box.add_.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings)==1
    assert BaseDomainError.MESSAGE_BOX_FAILLED.value in output.warnings
    