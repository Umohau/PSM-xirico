import pytest
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.DTOs.orders_DTOS import OrderUpdateDTO
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.use_cases.orders_use_cases.change_order_bird import ChangeOrderBird
from Projeto_xirico.exc import EntityNotFoundError

@pytest.fixture
def change_order_bird(mock_repo, mock_audit, mock_profile):
    return ChangeOrderBird(repo= mock_repo, profile= mock_profile, audit=mock_audit)

bird= OrderUpdateDTO(id='ORD123', bird=3, otp='000000')


def test_change_order_bird_sucess(mock_repo, mock_audit, change_order_bird):
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    res= change_order_bird.execute(bird)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) ==0


def test_change_order_birb_order_not_found(mock_repo, mock_audit, change_order_bird):
    mock_repo.get_order_oid.side_effect= EntityNotFoundError
    res= change_order_bird.execute(bird)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value


def test_change_order_bir_db_error(mock_repo, mock_audit, change_order_bird):
    mock_repo.update.side_effect= IntegrityError('error', (9), 'main')
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    res= change_order_bird.execute(bird)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value



def test_change_order_bir_db_conection_error(mock_repo, mock_audit, change_order_bird):
    mock_repo.update.side_effect= OperationalError('error', (9), 'main')
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    res= change_order_bird.execute(bird)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_change_order_bird_audit_failled(mock_repo, mock_audit, change_order_bird):
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    res= change_order_bird.execute(bird)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings