import pytest
from result import is_ok, is_err
from Projeto_xirico.use_cases.client_use_cases.client_update_telephone_by_id import ClientUpdateTelephoneBYId
from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.DTOs.client_DTOs import ClientUpdateDTO

telefone= ClientUpdateDTO(client_id=1, telephone='+258865050678')


@pytest.fixture
def client_update_telephone_by_id(mock_repo, mock_audit, mock_profile):
    return ClientUpdateTelephoneBYId(repo= mock_repo, audit= mock_audit, profile= mock_profile)


def test_client_update_telephone_sucess(
        mock_repo,
        mock_audit,
        client_update_telephone_by_id
):
    
    mock_repo.update.return_value=1
    mock_repo.search_id.return_value= {'id':1, 'telefone': '+258853704474'}
    res= client_update_telephone_by_id.execute(telefone)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called()
    mock_repo.search_id.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings)==0


def test_client_update_telephonr_db_conexion_error(
        mock_repo,
        mock_audit,
        client_update_telephone_by_id
):
    mock_repo.update.side_effect= OperationalError('erro', (9), "main")
    res= client_update_telephone_by_id.execute(telefone)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_not_called()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_client_update_telephone_db_error(
        mock_repo,
        mock_audit,
        client_update_telephone_by_id
):
    mock_repo.update.side_effect= DatabaseError('erro', (9), "main")
    res= client_update_telephone_by_id.execute(telefone)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_not_called()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_client_update_telephone_audit_failled(
        mock_repo,
        mock_audit,
        client_update_telephone_by_id
):
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.update.return_value=1
    mock_repo.search_id.return_value= {'id':3, 'telefone': '+258853705383'}
    res=client_update_telephone_by_id.execute(telefone)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called()
    mock_repo.search_id.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value