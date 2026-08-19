import pytest
from result import is_err, is_ok
from sqlalchemy.exc import DatabaseError, OperationalError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, BirdsError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.use_cases.catalog_use_cases.recovery_bird_in_catalog import RecoveryBirdInCtalog


@pytest.fixture
def recovery_bird_in_catalog(mock_audit, mock_profile, mock_repo):
    return RecoveryBirdInCtalog(
        repo= mock_repo,
        audit= mock_audit,
        profile= mock_profile
    )


def test_recovery_bird_in_catalog_sucess(
        recovery_bird_in_catalog,
        mock_repo,
        mock_audit
):
    mock_repo.recovery.return_value= 1
    res= recovery_bird_in_catalog.execute(1)
    output= res.unwrap()
    mock_repo.recovery.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) == 0


def test_recovery_bird_in_catalog_db_error(
        recovery_bird_in_catalog,
        mock_repo,
        mock_audit
):
    mock_repo.recovery.side_effect= OperationalError('erro', (4), 'main')
    res= recovery_bird_in_catalog.execute(1)
    output= res.unwrap_err()
    mock_repo.recovery.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value

def test_recovery_bird_bird_not_found(
        recovery_bird_in_catalog,
        mock_repo,
        mock_audit
):
    mock_repo.recovery.side_effect= EntityNotFoundError
    res= recovery_bird_in_catalog.execute(200)
    output= res.unwrap_err()
    mock_repo.recovery.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BirdsError)
    assert output.value == BirdsError.BIRD_NOT_FOUND.value


def test_recovery_bird_in_catalog__audit_failled(
        recovery_bird_in_catalog,
        mock_repo,
        mock_audit
):
    mock_repo.recovery.return_value= 1
    mock_audit.auditar.side_effect= OperationalError('erro', (894), 'main')
    res= recovery_bird_in_catalog.execute(1)
    output= res.unwrap()
    mock_repo.recovery.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.DB_CONECTION_ERROR.value in output.warnings
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
