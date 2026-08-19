import pytest
from result import is_err, is_ok
from sqlalchemy.exc import OperationalError
from Projeto_xirico.exc import EmptyTableError
from Projeto_xirico.domain_exceptions import BaseDomainError
from Projeto_xirico.DTOs.bird_DTOs import BirdGetResponseDTO
from Projeto_xirico.use_cases.catalog_use_cases.show_catalog import ShowCatalog

dados={
    'id':3,
    'nome_cientifico':'critagra mozambicus',
    'nome_comum':'xirico',
    'especie':'crithagra',
    'preco':5
}

@pytest.fixture
def show_catalog(mock_repo):
    return ShowCatalog(repo= mock_repo)


def test_show_catalog_sucess(show_catalog, mock_repo):
    mock_repo.search_all.return_value= [dados, dados]
    res= show_catalog.execute()
    output= res.unwrap()
    mock_repo.search_all.assert_called()
    assert is_ok(res)
    assert isinstance (output, list)
    assert isinstance(output[0], BirdGetResponseDTO)


def test_show_catalog_db_conexion_error(show_catalog, mock_repo):
    mock_repo.search_all.side_effect= OperationalError('erro', (9), 'main')
    res= show_catalog.execute()
    output= res.unwrap_err()
    mock_repo.search_all.assert_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_show_catalog_empty_table(show_catalog, mock_repo):
    mock_repo.search_all.side_effect= EmptyTableError
    res= show_catalog.execute()
    output= res.unwrap_err()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert BaseDomainError.EMPTY_TABLE.value == output.value