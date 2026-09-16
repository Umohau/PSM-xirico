import pytest
from unittest.mock import PropertyMock
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.DTOs.orders_DTOS import OrderUpdateDTO
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.use_cases.orders_use_cases.update_quantity_bird_off_order import UpdateQuantityBirdOfOrder
from Projeto_xirico.exc import EntityNotFoundError

@pytest.fixture
def update_bird_quantity(mock_repo, mock_audit, mock_profile):
    return UpdateQuantityBirdOfOrder(repo= mock_repo, profile= mock_profile, audit=mock_audit)

bird= OrderUpdateDTO(id='ORD123', quantity=300)


def test_update_order_bird_quantity_sucess(mock_repo, mock_audit, update_bird_quantity):
    mock_repo.get_order_oid.return_value= {'quantidade': 200, 'gestor_id':3, 'estado': 'pendente'}
    mock_repo.update.return_value= 1
    res= update_bird_quantity.execute(bird)
    mock_repo.get_order_oid.assert_called()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) == 0


def test_update_order_bird_quantity_permission_denied(mock_profile, mock_repo, mock_audit, update_bird_quantity):
    type(mock_profile).ADM= PropertyMock(return_value=False)
    res= update_bird_quantity.execute(bird)
    mock_repo.get_order_oid.assert_called()
    mock_repo.update.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value


def test_update_order_quantity_order_not_found(mock_repo, mock_audit, update_bird_quantity):
    mock_repo.get_order_oid.side_effect= EntityNotFoundError
    res= update_bird_quantity.execute(bird)
    mock_repo.get_order_oid.assert_called()
    mock_repo.update.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value


def test_update_order_bird_quantity_db_conection_error(mock_profile, mock_repo, mock_audit, update_bird_quantity):
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_repo.get_order_oid.return_value= {'quantidade': 200, 'gestor_id':3, 'estado': 'pendente'}
    mock_repo.update.side_effect=OperationalError('error', (9), 'main')
    res= update_bird_quantity.execute(bird)
    mock_repo.get_order_oid.assert_called()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value



def test_update_order_bird_quantity_db_error(mock_profile, mock_repo, mock_audit, update_bird_quantity):
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_repo.get_order_oid.return_value= {'quantidade': 200, 'gestor_id':3, 'estado': 'pendente'}
    mock_repo.update.side_effect=DatabaseError('error', (9), 'main')
    res= update_bird_quantity.execute(bird)
    mock_repo.get_order_oid.assert_called()
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value