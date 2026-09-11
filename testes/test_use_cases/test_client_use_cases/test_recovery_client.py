import pytest
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.use_cases.client_use_cases.recovery_client import RecoveryClient

@pytest.fixture
def recovery_client(mock_repo, mock_profile, mock_audit):
    return RecoveryClient(repo= mock_repo, profile= mock_profile, audit= mock_audit)

email= "clientedeteste@gmail.com"


def test_recovery_client_sucess(recovery_client,mock_audit, mock_repo):
    mock_repo.reactivate.return_value=1
    mock_repo.search_email.return_value= {'id':3}
    res=recovery_client.execute(email)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(res.unwrap(), UpdateOutputDTO)


def test_recovery_client_entity_not_found(recovery_client,mock_audit, mock_repo):
    mock_repo.reactivate.side_effect= EntityNotFoundError
    res=recovery_client.execute(email)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, ClientError)
    assert output.value == ClientError.CLIENT_NOT_FOUND_ERROR.value


def test_recovery_client_db_conexion_error(recovery_client, mock_repo, mock_audit):
    mock_repo.reactivate.side_effect= OperationalError('erro', (9), "main")
    res=recovery_client.execute(email)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_recovery_client_db_error(recovery_client, mock_repo, mock_audit):
    mock_repo.reactivate.side_effect= DatabaseError('erro', (9), "main")
    res=recovery_client.execute(email)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_recovery_client_audit_failled(recovery_client, mock_repo, mock_audit):
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.reactivate.return_value=1
    mock_repo.search_email.return_value= {'id':3}
    res=recovery_client.execute(email)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
