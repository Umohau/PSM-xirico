import pytest
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.DTOs.bird_DTOs import BirdsUpdateDTO
from Projeto_xirico.use_cases.catalog_use_cases.update_cientific_bird_name_in_catalog import UpdateBirdCientificNameInCatalog
from Projeto_xirico.domain_exceptions import BaseDomainError, BirdsError
from Projeto_xirico.exc import EntityNotFoundError

dados=BirdsUpdateDTO(
    bird_id=1,
    cientific_name= 'crithagra otrogulares'
)


@pytest.fixture
def update_bird_cientific_name(mock_repo, mock_audit, mock_profile):
    return UpdateBirdCientificNameInCatalog(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


def test_update_bird_cientific_name_in_catalog_by_id_sucess(
        mock_repo,
        mock_audit,
        update_bird_cientific_name
):
    mock_repo.search_id.return_value= {'nome_cientifico': 'crithagra mozambicus'}
    mock_repo.update.return_value= 1
    res= update_bird_cientific_name.execute(dados_in= dados)
    output= res.unwrap()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) == 0


def test_update_bird_cientific_name_bird_not_found(
        mock_repo,
        mock_audit,
        update_bird_cientific_name
):
    mock_repo.update.side_effect= EntityNotFoundError
    res= update_bird_cientific_name.execute(dados_in= dados)
    output= res.unwrap_err()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BirdsError)
    assert output.value == BirdsError.BIRD_NOT_FOUND.value


def test_update_bird_cientific_name_audit_failled(
        mock_audit,
        mock_repo,
        update_bird_cientific_name
):
    mock_repo.search_id.return_value= {'nome_cientifico': 'crithagra mozambicus'}
    mock_repo.update.return_value= 1
    mock_audit.auditar.side_effect= OperationalError('erro', (9), 'main')
    res= update_bird_cientific_name.execute(dados_in= dados)
    output= res.unwrap()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.DB_CONECTION_ERROR.value in output.warnings
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings


def test_update_bird_cientific_name_in_catalog_conexion_error(
        mock_repo,
        mock_audit,
        update_bird_cientific_name
):
    mock_repo.update.side_effect= OperationalError('erro', (9), "main")
    res= update_bird_cientific_name.execute(dados_in= dados)
    output= res.unwrap_err()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value
    