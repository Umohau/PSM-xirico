import pytest
from result import is_ok, is_err
from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.use_cases.client_use_cases.delete_client_by_id import DeleteClientById


@pytest.fixture
def delete_client_by_id(mock_audit, mock_repo, mock_profile):
    return DeleteClientById(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )

id=1


def test_delete_cliente_by_id_sucess(delete_client_by_id, mock_repo, mock_audit):
    res= delete_client_by_id.execute(id)
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(res.unwrap(), UpdateOutputDTO)

def test_delete_cliente_by_id_entity_not_found(delete_client_by_id, mock_repo, mock_audit):
    mock_repo.delete.side_effect= EntityNotFoundError
    res= delete_client_by_id.execute(id)
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, ClientError)
    assert output.value == ClientError.CLIENT_NOT_FOUND_ERROR.value


def test_delete_cliete_by_id_conection_error(delete_client_by_id, mock_repo, mock_audit):
    mock_repo.delete.side_effect= OperationalError('erro', (9), "main")
    res= delete_client_by_id.execute(id)
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_delete_client_by_id_db_error(delete_client_by_id, mock_repo, mock_audit):
    mock_repo.delete.side_effect= DatabaseError('erro', (9), "main")
    res= delete_client_by_id.execute(id)
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_delete_client_by_id_uadit_failled(delete_client_by_id, mock_repo, mock_audit):
    mock_audit.auditar.side_effect= FileNotFoundError
    res= delete_client_by_id.execute(id)
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
