import pytest
from result import is_err, is_ok

from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.exc import DuplicateError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.DTOs.client_DTOs import ClientRegistDTO
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO
from Projeto_xirico.use_cases.client_use_cases.regist_new_client import RegistNEwClient



@pytest.fixture
def regist_new_client(mock_repo, mock_profile, mock_audit):
    return RegistNEwClient(
        repo= mock_repo,
        audit= mock_audit,
        profile= mock_profile
    )

dados=ClientRegistDTO(
    name='ricardo',
    email='ricardo@gmail.com',
    domain='ricardo corporation',
    telephone='+258867060896',
    address='maputo,  rua 33'
)

def test_regist_new_client_sucess(regist_new_client, mock_repo, mock_audit):
    res=regist_new_client.execute(dados)
    assert is_ok(res)
    output= res.unwrap()
    mock_repo.insert.assert_called_once_with(dados)
    mock_audit.auditar.assert_called()
    assert isinstance(output, InsertOutputDTO)


def test_regist_new_client_check_unique_failled(regist_new_client, mock_repo, mock_audit):
    mock_repo.insert.side_effect= DuplicateError
    res= regist_new_client.execute(dados)
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, ClientError)
    assert output.value == ClientError.CLIENT_ALREAD_EXISTS_ERROR.value


def test_regist_new_client_audit_failled(mock_audit, mock_repo, regist_new_client):
    mock_audit.auditar.side_effect= FileNotFoundError
    res= regist_new_client.execute(dados)
    mock_repo.insert.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert BaseDomainError.AUDIT_FAILED.value in  output.warnings

def test_regist_new_client_db_conection_error(mock_audit, mock_repo, regist_new_client):
    mock_repo.insert.side_effect= OperationalError('erro', (9), "main")
    res= regist_new_client.execute(dados)
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_regist_new_client_DB_error(mock_audit, mock_repo, regist_new_client):
    mock_repo.insert.side_effect= DatabaseError('erro', (9), "main")
    res= regist_new_client.execute(dados)
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value
