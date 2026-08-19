import pytest
from result import is_err, is_ok
from sqlalchemy.exc import OperationalError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.domain_exceptions import BaseDomainError, BirdsError
from Projeto_xirico.DTOs.bird_DTOs import BirdGetResponseDTO
from Projeto_xirico.use_cases.catalog_use_cases.search_birds import SearchBirdById, SearchBirdByName


dados={
    'id':3,
    'nome_cientifico':'critagra mozambicus',
    'nome_comum':'xirico',
    'especie':'crithagra',
    'preco':5
}

@pytest.fixture
def search_bird_by_id(mock_repo):
    return SearchBirdById(repo= mock_repo)

@pytest.fixture
def search_bird_by_name(mock_repo):
    return SearchBirdByName(repo= mock_repo)



def test_search_bird_by_name_sucess(search_bird_by_name, mock_repo):
    mock_repo.search_name.return_value= [dados, dados]
    res= search_bird_by_name.execute('crithagra')
    output= res.unwrap()
    mock_repo.search_name.assert_called()
    assert is_ok(res)
    assert isinstance (output, list)
    assert isinstance(output[0], BirdGetResponseDTO)
    assert len(output)==2



def test_search_bird_by_name_bird_not_found(
        mock_repo,
        search_bird_by_name
):
    mock_repo.search_name.side_effect= EntityNotFoundError
    res= search_bird_by_name.execute('pombo')
    output= res.unwrap_err()
    mock_repo.search_name.assert_called()
    assert is_err(res)
    assert isinstance(output, BirdsError)
    assert output.value == BirdsError.BIRD_NOT_FOUND.value


def test_search_bird_by_name_DB_conexion_error(mock_repo, search_bird_by_name):
    mock_repo.search_name.side_effect= OperationalError('errpo', (0), 'main')
    res= search_bird_by_name.execute(1)
    output= res.unwrap_err()
    mock_repo.search_name.assert_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert BaseDomainError.DB_CONECTION_ERROR.value == output.value


#testes para o use_case search_bird_by_id
def test_search_bird_by_id_sucess(search_bird_by_id, mock_repo):
    mock_repo.search_id.return_value= dados
    res= search_bird_by_id.execute(3)
    output= res.unwrap()
    mock_repo.search_id.assert_called()
    assert is_ok(res)
    assert isinstance (output, BirdGetResponseDTO)


def test_search_bird_by_id_bird_not_found(
        mock_repo,
        search_bird_by_id
):
    mock_repo.search_id.side_effect= EntityNotFoundError
    res= search_bird_by_id.execute(400)
    output= res.unwrap_err()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    assert isinstance(output, BirdsError)
    assert output.value == BirdsError.BIRD_NOT_FOUND.value


def test_search_bird_by_id_DB_conexion_error(mock_repo, search_bird_by_id):
    mock_repo.search_id.side_effect= OperationalError('errpo', (0), 'main')
    res= search_bird_by_id.execute(1)
    output= res.unwrap_err()
    mock_repo.search_id.assert_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert BaseDomainError.DB_CONECTION_ERROR.value == output.value
