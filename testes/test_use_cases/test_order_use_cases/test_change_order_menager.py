import pytest
from unittest.mock import PropertyMock
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.DTOs.orders_DTOS import OrderUpdateDTO
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.use_cases.orders_use_cases.change_order_maneger import ChangeOrderMenager
from Projeto_xirico.exc import EntityNotFoundError, InvalidOtpError


@pytest.fixture
def change_order_manager(mock_auth, mock_repo, mock_audit, mock_profile, mock_message_box):
    return ChangeOrderMenager(operator=mock_repo, auth= mock_auth, repo= mock_repo, profile= mock_profile, audit= mock_audit, message_box= mock_message_box)

menager= OrderUpdateDTO(id='ORD123', menager_id=3, otp='00000000')



def test_change_order_menager_sucess(mock_auth, mock_repo, mock_audit, mock_message_box, change_order_manager, mock_profile):
    #configura o retorno dos mocks
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_auth.verificar_otp.return_value= True
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}

    #executa a operacao
    res= change_order_manager.execute(menager)

    #verifica as chamadas e faz ass acercecoes
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_message_box.add_.assert_called()
    mock_auth.verificar_otp.assert_called_with(menager.otp)
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert len(output.warnings) ==0



def test_change_order_menager_order_not_found(mock_repo, mock_audit, mock_message_box, change_order_manager):
    mock_repo.get_order_oid.side_effect= EntityNotFoundError
    res= change_order_manager.execute(menager)
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_not_called()
    mock_message_box.add_.assert_not_called()
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, OrderError)
    assert output.value == OrderError.ORDER_NOT_FOUND_ERROR.value


def test_change_order_menager_invalid_input_data(mock_auth, mock_profile, mock_repo, mock_message_box, mock_audit, change_order_manager):
    #configura o retorno dos mocks
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_auth.verificar_otp.return_value= True
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    mock_repo.update.side_effect= IntegrityError('error', (9), 'main')

    #executa a operacao
    res= change_order_manager.execute(menager)

    #verifica as chamadas e faz as acercoes
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_message_box.add_.assert_not_called()
    mock_auth.verificar_otp.assert_called_with(menager.otp)
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.INVALID_INPUT_DATA.value



def test_change_order_menager_db_conection_error(mock_auth, mock_profile, mock_repo, mock_message_box, mock_audit, change_order_manager):
    #configura o retorno dos mocks
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_auth.verificar_otp.return_value= True
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    mock_repo.update.side_effect= OperationalError('error', (9), 'main')

    #executa a operacao
    res= change_order_manager.execute(menager)

    #verifica as chamadas e faz as acercoes
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_message_box.add_.assert_not_called()
    mock_auth.verificar_otp.assert_called_with(menager.otp)
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_change_order_menager_audit_failled(mock_auth, mock_profile, mock_repo, mock_message_box, mock_audit, change_order_manager):
    #configura o retorno dos mocks
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_auth.verificar_otp.return_value= True
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.update.return_value=1

    #executa a operacao
    res= change_order_manager.execute(menager)

    #verifica as chamadas e faz as acercoes
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_message_box.add_.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings



def test_change_order_menager_message_box_failled_failled(mock_auth, mock_profile, mock_repo, mock_message_box, mock_audit, change_order_manager):
    #configura o retorno dos mocks
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_auth.verificar_otp.return_value= True
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    mock_message_box.add_.side_effect= OperationalError('error', (9), 'main')
    mock_repo.update.return_value=1

    #executa a operacao
    res= change_order_manager.execute(menager)

    #verifica as chamadas e faz as acercoes
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_called()
    mock_message_box.add_.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.MESSAGE_BOX_FAILLED.value in output.warnings



def test_change_order_menager_permission_denied(mock_auth, mock_profile, mock_repo, mock_message_box, mock_audit, change_order_manager):
    #configura o retorno dos mocks
    type(mock_profile).ADM= PropertyMock(return_value=False)
    mock_auth.verificar_otp.return_value= True
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    mock_repo.update.return_value=1

    #executa a operacao
    res= change_order_manager.execute(menager)

    #verifica as chamdas e faz as acercoes
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_not_called()
    mock_message_box.add_.assert_not_called()
    mock_auth.verificar_otp.assert_not_called
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value



def test_change_order_menager_otp_invalido(mock_auth, mock_profile, mock_repo, mock_message_box, mock_audit, change_order_manager):
    #configura o retorno dos mocks
    type(mock_profile).ADM= PropertyMock(return_value=True)
    mock_auth.verificar_otp.side_effect= InvalidOtpError
    mock_repo.update.return_value=1
    mock_repo.get_order_oid.return_value= {'gestor_id':3, 'ave_id':1, 'estado': 'pendente'}
    mock_repo.update.return_value=1

    #executa a operacao
    res= change_order_manager.execute(menager)

    #verifica as chamdas e faz as acercoes
    mock_repo.get_order_oid.assert_called_once()
    mock_repo.update.assert_not_called()
    mock_message_box.add_.assert_not_called()
    mock_auth.verificar_otp.assert_not_called
    mock_audit.auditar.assert_not_called()
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.INCORRECT_OTP_ERROR.value
