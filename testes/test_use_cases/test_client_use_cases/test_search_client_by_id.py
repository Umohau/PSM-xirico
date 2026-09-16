import pytest
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.use_cases.client_use_cases.search_client_by_id import SearchClientById
from Projeto_xirico.DTOs.client_DTOs import ClientGetResponseDTO


dados={
    'id':1,
    'nome': 'cliente1',
    'dominio': 'empresa do cliente lda',
    'endereco': 'mocambique, maouto, rua das flores',
    'telefone': '+258852703354',
    'email': 'cliente1@gmail.com'
}

id= 1

@pytest.fixture
def search_client_by_id(mock_audit, mock_repo, mock_profile):
    return SearchClientById(repo= mock_repo, profile= mock_profile)



def test_search_client_by_id_sucess(mock_repo, search_client_by_id):
    mock_repo.search_by_id.return_value= dados
    res= search_client_by_id.execute(id)
    mock_repo.search_by_id.assert_called()
    assert is_ok(res)
    assert isinstance(res.unwrap(), ClientGetResponseDTO)


def test_search_client_by_id_client_not_found_error(mock_repo, search_client_by_id):
    mock_repo.search_by_id.side_effect= EntityNotFoundError
    res= search_client_by_id.execute(id)
    mock_repo.search_by_id.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, ClientError)
    assert output.value == ClientError.CLIENT_NOT_FOUND_ERROR.value


def test_search_client_by_id_db_conection_error(mock_repo, search_client_by_id):
    mock_repo.search_by_id.side_effect= OperationalError('eror', (9), 'main')
    res= search_client_by_id.execute(id)
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_search_client_by_id_db_error(mock_repo, search_client_by_id):
    mock_repo.search_by_id.side_effect= DatabaseError('eror', (9), 'main')
    res= search_client_by_id.execute(id)
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value
