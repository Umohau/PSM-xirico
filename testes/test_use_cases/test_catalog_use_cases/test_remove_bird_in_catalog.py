import pytest
from result import is_ok, is_err
from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.use_cases.catalog_use_cases.remove_bird_in_catalog_by_id import RemoveBirdsInCatalogById
from Projeto_xirico.DTOs.bird_DTOs import BirdsUpdateDTO
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, BirdsError
from Projeto_xirico.exc import EntityNotFoundError


@pytest.fixture
def remove_bird_in_catalog_by_id(mock_repo, mock_profile, mock_audit):
    return RemoveBirdsInCatalogById(
        profile= mock_profile,
        audit= mock_audit,
        repo= mock_repo
    )


def test_remove_bird_in_catalog_by_id_sucess(
        remove_bird_in_catalog_by_id,
        mock_repo,
        mock_audit
):
    
    res= remove_bird_in_catalog_by_id.execute(1)
    output= res.unwrap()
    mock_repo.delete.assert_called_once()
    mock_audit.auditar.assert_called_once()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)


def test_remove_bird_in_catalog_by_id_DB_Error(
    mock_repo,
    mock_audit,
    remove_bird_in_catalog_by_id
):
    mock_repo.delete.side_effect= DatabaseError('erro', (9), 'main')
    res= remove_bird_in_catalog_by_id.execute(1)
    output= res.unwrap_err()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_remove__bird_in_catalog_by_id(
    remove_bird_in_catalog_by_id,
    mock_repo,
    mock_audit
):
    mock_repo.delete.side_effect= OperationalError('erro', (9), 'main')
    res= remove_bird_in_catalog_by_id.execute(1)
    output= res.unwrap_err()
    mock_repo.delete.assert_called_once()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value

def test_remove_bird_in_catalog_by_id_audit_failled(
    remove_bird_in_catalog_by_id,
    mock_repo,
    mock_audit
):
    mock_audit.auditar.side_effect= OperationalError('erro', (9), "main")
    res= remove_bird_in_catalog_by_id.execute(1)
    output=res.unwrap()
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.DB_CONECTION_ERROR.value in output.warnings
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings


def test_remove_bird_in_catalog_bird_not_found(
        remove_bird_in_catalog_by_id,
        mock_repo,
        mock_audit
):
    mock_repo.delete.side_effect= EntityNotFoundError
    res= remove_bird_in_catalog_by_id.execute(200)
    output= res.unwrap_err()
    mock_repo.deleteassert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BirdsError)
    assert output.value == BirdsError.BIRD_NOT_FOUND.value
