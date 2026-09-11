import pytest
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError
from Projeto_xirico.exc import EmptyTableError
from Projeto_xirico.domain_exceptions import BaseDomainError, ClientError
from Projeto_xirico.use_cases.client_use_cases.list_clients import ListClients
from Projeto_xirico.DTOs.client_DTOs import ClientGetResponseDTO

dados=[{
    'id':1,
    'nome': 'cliente1',
    'dominio': 'empresa do cliente lda',
    'endereco': 'mocambique, maouto, rua das flores',
    'telefone': '+258852703354',
    'email': 'cliente1@gmail.com'
}]


@pytest.fixture
def list_clients(mock_repo, mock_profile):
    return ListClients(repo= mock_repo, profile= mock_profile)


def test_list_clients_sucess(mock_repo, list_clients):
    mock_repo.search_all.return_value= dados
    res= list_clients.execute()
    mock_repo.search_all.assert_called()
    assert is_ok(res)
    assert isinstance(res.unwrap(), list)
    assert isinstance(res.unwrap()[0], ClientGetResponseDTO)

def test_list_clients_Empty_table_error(mock_repo, list_clients):
    mock_repo.search_all.side_effect= EmptyTableError
    res= list_clients.execute()
    mock_repo.search_all.assert_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.EMPTY_TABLE.value


def test_list_clients_db_conection_error(mock_repo, list_clients):
    mock_repo.search_all.side_effect= OperationalError('eror', (9), 'main')
    res= list_clients.execute()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value



def test_list_clients_db_error(mock_repo, list_clients):
    mock_repo.search_all.side_effect= DatabaseError('eror', (9), 'main')
    res= list_clients.execute()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value
