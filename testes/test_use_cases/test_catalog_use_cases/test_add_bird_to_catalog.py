import pytest
from result import is_ok, is_err
from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.DTOs.bird_DTOs import BirdsAddDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, BirdsError
from Projeto_xirico.exc import DuplicateError
from Projeto_xirico.use_cases.catalog_use_cases.add_bird_to_catalog import AddBirdToCatolog

dados= BirdsAddDTO(
    usual_name='xiricos',
    cientific_name='Crithagra mozambicus',
    bird_species='crithagra',
    bird_price=15,
)

@pytest.fixture
def add_bird_to_catalog(mock_repo, mock_audit, mock_profile):
    return AddBirdToCatolog(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )

def test_add_bird_to_catalog_sucess(add_bird_to_catalog, mock_repo, mock_audit):
    res= add_bird_to_catalog.execute(dados= dados)
    mock_repo.insert.assert_called_once()
    mock_audit.auditar.assert_called_once
    output=res.unwrap()
    assert is_ok(res)
    assert len(output.warnings) == 0


def test_add_bird_to_catalog_DB_Error(add_bird_to_catalog, mock_repo, mock_audit, mocker):
    mock_repo.insert.side_effect= DatabaseError('erro', (1,45,), 'main')
    res= add_bird_to_catalog.execute(dados= dados)
    err= res.unwrap_err()
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(err, BaseDomainError)
    assert err.value == BaseDomainError.DB_ERROR.value


def test_add_bird_to_catalog_DB_CONEXION_ERROR(mock_repo, mock_audit, add_bird_to_catalog):
    mock_repo.insert.side_effect= OperationalError('erro', (1,45,), 'main')
    res= add_bird_to_catalog.execute(dados= dados)
    err= res.unwrap_err()
    mock_repo.insert.assert_called_once()
    mock_audit.assert_not_called()
    assert is_err(res)
    assert isinstance(err, BaseDomainError)
    assert err.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_add_bird_to_catalog_uadit_failed(add_bird_to_catalog, mock_repo, mock_audit):
    mock_audit.auditar.side_effect= DatabaseError('erro', (1,45,), 'main')
    res= add_bird_to_catalog.execute(dados= dados)
    result= res.unwrap()
    mock_repo.insert.assert_called_once()
    mock_audit.auditar.assert_called_once()
    assert is_ok(res)
    assert BaseDomainError.AUDIT_FAILED.value in result.warnings
    assert BaseDomainError.DB_ERROR.value in result.warnings


def test_add_bird_to_catalog_bird_alread_exists(
        add_bird_to_catalog,
        mock_repo,
        mock_audit
):
    mock_repo.insert.side_effect= DuplicateError
    res= add_bird_to_catalog.execute(dados)
    output= res.unwrap_err()
    mock_repo.insert.assert_called()
    mock_audit.auditoria.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BirdsError)
    assert output.value == BirdsError.BIRD_ALREAD_EXISTS.value
