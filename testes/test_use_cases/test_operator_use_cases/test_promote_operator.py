import pytest
from unittest.mock import PropertyMock
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError

from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.exc import PermissionDeniedError, CredentialsError, EntityNotFoundError
from Projeto_xirico.use_cases.operator_use_cases.promote_operator import PromoteOperator


@pytest.fixture
def promote_operator(mock_message_box, mock_repo, mock_profile, mock_audit):
    return PromoteOperator(
        message_box= mock_message_box,
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


def test_promote_operator_sucess(
    promote_operator,
    mock_message_box,
    mock_audit,
    mock_profile,
    mock_repo
):
    mock_repo.update.return_value=1
    id=1
    res= promote_operator.execute(id) #executa o metodo a testar
    output= res.unwrap()
    #verifica as chamadas aos componentes do use_case
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) ==0


def test_promote_operator_permission_denied(
    promote_operator,
    mock_message_box,
    mock_audit,
    mock_profile,
    mock_repo
):
    id=2
    type(mock_profile).ADM= PropertyMock(return_value=False) #faz a property ADM e profile retornar False
    res= promote_operator.execute(id) #executa o metodo a testar
    output= res.unwrap_err()
    #verifica as chamadas aos componentes do use_case
    mock_repo.update.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value


def test_promote_operator_db_conection_error(
    promote_operator,
    mock_message_box,
    mock_audit,
    mock_profile,
    mock_repo
):
    mock_repo.update.side_effect= OperationalError('error', (9), 'main')
    res= promote_operator.execute(id) #executa o metodo a testar
    output= res.unwrap_err()
    #verifica as chamadas aos componentes do use_case
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_promote_operator_audit_failled(
    promote_operator,
    mock_message_box,
    mock_audit,
    mock_profile,
    mock_repo
):
    id=1
    mock_repo.update.return_value=1
    mock_audit.auditar.side_effect= FileNotFoundError
    res= promote_operator.execute(id) #executa o metodo a testar
    output= res.unwrap()
    #verifica as chamadas aos componentes do use_case
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()
    mock_message_box.add_.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
    assert len(output.warnings) == 1


def test_promote_operator_message_box_failled(
    promote_operator,
    mock_message_box,
    mock_audit,
    mock_profile,
    mock_repo
):
    id=1
    mock_repo.update.return_value=1
    mock_message_box.add_.side_effect= DatabaseError('error', (9), 'main')
    res= promote_operator.execute(id) #executa o metodo a testar
    output= res.unwrap()
    #verifica as chamadas aos componentes do use_case
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()
    mock_message_box.add_.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.MESSAGE_BOX_FAILLED.value in output.warnings
    assert len(output.warnings) == 1