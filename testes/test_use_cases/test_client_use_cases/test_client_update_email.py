import pytest
from result import is_ok, is_err
from Projeto_xirico.use_cases.client_use_cases.client_update_email import ClientUpdateEmail
from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.DTOs.client_DTOs import ClientUpdateDTO


email= ClientUpdateDTO(client_id=1, email='novoemail@gmail.com')

@pytest.fixture
def client_update_email(mock_repo, mock_profile, mock_audit):
    return ClientUpdateEmail(repo= mock_repo, profile= mock_profile, audit= mock_audit)


def test_update_client_email_sucess(
        mock_repo,
        mock_audit,
        client_update_email
):
    mock_repo.update.return_value=1
    mock_repo.search_id.return_value= {'id':1, 'email': 'muhau@gmail.com'}
    res= client_update_email.execute(email)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called()
    mock_repo.search_id.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings)==0


def test_client_update_email_db_conexion_error(
        mock_repo,
        mock_audit,
        client_update_email
):
    mock_repo.update.side_effect= OperationalError('erro', (9), "main")
    res= client_update_email.execute(email)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_not_called()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value

def test_client_update_email_db_error(
        mock_repo,
        mock_audit,
        client_update_email
):
    mock_repo.update.side_effect= DatabaseError('erro', (9), "main")
    res= client_update_email.execute(email)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_not_called()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_client_update_email_audit_failled(
        mock_repo,
        mock_audit,
        client_update_email
):
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.update.return_value=1
    mock_repo.search_id.return_value= {'id':3, 'email': 'rua das flores'}
    res=client_update_email.execute(email)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called()
    mock_repo.search_id.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
    