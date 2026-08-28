import pytest
from unittest.mock import PropertyMock
from result import is_ok, is_err

from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import OperationalError,DatabaseError

from Projeto_xirico.use_cases.operator_use_cases.regist_new_operator import RegistNewOperator
from Projeto_xirico.DTOs.operator_DTOs import RegistOperatorDTO
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.exc import PermissionDeniedError, InvalidOtpError, DuplicateError



@pytest.fixture
def regis_new_operator(
    mock_repo,
    mock_audit,
    mock_auth,
    mock_profile,
    mock_message_box
):
    return RegistNewOperator(
        repo= mock_repo,
        auth= mock_auth,
        message_box= mock_message_box,
        profile= mock_profile,
        audit= mock_audit
    )


@pytest.fixture
def dados():
    return RegistOperatorDTO(
        operator_name='umohau',
        phone_number='+258852702385',
        operator_email= 'exemplo@gmail.com',
        morada= 'maputo,Moamba, Bairro exemplo',
        BI='100234567213A',
        codigo='00000000' 
    )


def test_regist_new_operator_sucess(
        regis_new_operator,
        mock_repo,
        mock_auth,
        mock_audit,
        mock_profile,
        mock_message_box,
        dados
):
    
    res= regis_new_operator.execute(dados) #executa a operacao de cadastro
    output= res.unwrap()
    mock_repo.check_unique.assert_called()
    mock_auth.verificar_otp.assert_called_with(dados.otp)
    mock_repo.insert.assert_called_once()
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()
    assert is_ok(res)
    assert isinstance(output, InsertOutputDTO)
    assert len(output.warnings) == 0


def test_regist_new_operator_permission_denied(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    dados
):
    type(mock_profile).ADM= PropertyMock(return_value= False)
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.check_unique.assert_not_called()
    mock_repo.insert.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value


def test_regist_new_operator_duplicate_email(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    dados
):
    mock_repo.check_unique.side_effect= DuplicateError('o email fornecido ja se encontra cadastrado')
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.insert.assert_not_called()
    mock_repo.insert.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, OperatorError)
    assert output.value == OperatorError.OPERATOR_DUPLICATE_EMAIL_ERROR.value



def test_regist_new_operator_duplicate_telefone(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    dados
):
    mock_repo.check_unique.side_effect= DuplicateError('o telefone fornecido ja se encontra cadastrado')
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.insert.assert_not_called()
    mock_repo.insert.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, OperatorError)
    assert output.value == OperatorError.OPERATOR_DUPLICATE_TELEFONE_ERROR.value


def test_regist_new_operator_duplicate_BI(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    dados
):
    mock_repo.check_unique.side_effect= DuplicateError('o BI fornecido ja se encontra cadastrado')
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.insert.assert_not_called()
    mock_repo.insert.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, OperatorError)
    assert output.value == OperatorError.OPERATOR_DUPLICATE_BI_ERROR.value


def test_regist_new_operator_invalid_otp(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    mock_auth,
    dados
):
    mock_auth.verificar_otp.side_effect= InvalidTokenError
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.INVALID_OTP_ERROR.value
    

def test_regist_new_operator_incorrect_otp(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    mock_auth,
    dados
):
    mock_auth.verificar_otp.side_effect= InvalidOtpError
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.INCORRECT_OTP_ERROR.value



def test_regist_new_operator_audit_failed(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    mock_auth,
    dados
):
    mock_audit.auditar.side_effect= DatabaseError('erro', (9), 'main')
    res= regis_new_operator.execute(dados)
    output= res.unwrap()
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_called()
    mock_message_box.add_.assert_called()
    assert is_ok(res)
    assert isinstance(output, InsertOutputDTO)
    assert len(output.warnings) ==1
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings



def test_regist_new_operator_audit_failed(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    mock_auth,
    dados
):
    mock_audit.auditar.side_effect= DatabaseError('erro', (9), 'main')
    res= regis_new_operator.execute(dados)
    output= res.unwrap()
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_called()
    mock_message_box.add_.assert_called()
    assert is_ok(res)
    assert isinstance(output, InsertOutputDTO)
    assert len(output.warnings) ==1
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings


def test_regist_new_operator_message_box_failled(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    mock_auth,
    dados
):
    mock_message_box.add_.side_effect= DatabaseError('erro', (9), 'main')
    res= regis_new_operator.execute(dados)
    output= res.unwrap()
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_called()
    mock_message_box.add_.assert_called()
    assert is_ok(res)
    assert isinstance(output, InsertOutputDTO)
    assert len(output.warnings) ==1
    assert BaseDomainError.MESSAGE_BOX_FAILLED.value in output.warnings
    

def test_regist_new_operator_db_conexion_error(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    mock_auth,
    dados
):
    mock_repo.insert.side_effect= OperationalError('erro', (9), 'main')
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_regist_new_operator_db_error(
    regis_new_operator,
    mock_repo,
    mock_audit,
    mock_profile,
    mock_message_box,
    mock_auth,
    dados
):
    
    mock_repo.insert.side_effect= DatabaseError('erro', (9), 'main')
    res= regis_new_operator.execute(dados)
    output= res.unwrap_err()
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value
