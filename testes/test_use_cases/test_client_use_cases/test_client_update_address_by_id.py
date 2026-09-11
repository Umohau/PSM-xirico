import pytest
from result import is_ok, is_err
from Projeto_xirico.use_cases.client_use_cases.client_update_address_by_id import ClientUpdateAdressById
from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.DTOs.client_DTOs import ClientUpdateDTO

address= ClientUpdateDTO(client_id=1, address='rua das flores, q2, casa27')


@pytest.fixture
def client_update_address_by_id(mock_repo, mock_profile, mock_audit):
    return ClientUpdateAdressById(repo= mock_repo, audit= mock_audit, profile= mock_profile)


def test_update_client_address_by_id_sucess(client_update_address_by_id, mock_audit, mock_repo):
    mock_repo.update.return_value=1
    mock_repo.search_id.return_value= {'id':3, 'endereco': 'rua das flores'}
    res= client_update_address_by_id.execute(address)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called()
    mock_repo.search_id.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings)==0


def test_update_client_address_by_id_db_conextion_error(
        client_update_address_by_id,
        mock_audit,
        mock_repo):
    mock_repo.update.side_effect= OperationalError('erro', (9), "main")
    res= client_update_address_by_id.execute(address)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_not_called()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_update_client_address_by_id_db_error(
    client_update_address_by_id,
        mock_audit,
        mock_repo):
    mock_repo.update.side_effect= DatabaseError('erro', (9), "main")
    res= client_update_address_by_id.execute(address)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_not_called()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value



def test_update_client_address__by_id_audit_failled(
        client_update_address_by_id,
        mock_audit,
        mock_repo):
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.update.return_value=1
    mock_repo.search_id.return_value= {'id':3, 'endereco': 'rua das flores'}
    res=client_update_address_by_id.execute(address)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called()
    mock_repo.search_id.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
