import pytest
from unittest.mock import PropertyMock
from result import is_err, is_ok
from sqlalchemy.exc import OperationalError

from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.DTOs.operator_DTOs import ReactivateOperatorDTO
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.exc import PermissionDeniedError, EntityNotFoundError, InvalidOtpError
from Projeto_xirico.use_cases.operator_use_cases.reactivate_operator_by_email import ReactivateOperatorByEmail


@pytest.fixture
def reactivate_operator_by_email(mock_audit, mock_auth, mock_message_box,  mock_profile, mock_repo):
    return ReactivateOperatorByEmail(
        message_box= mock_message_box,
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit,
        auth= mock_auth
    )

dto=ReactivateOperatorDTO(
    codigo='00000000',
    email= "emailTeste@gmail.com"
)

operador: dict= {
    'id':1,
    'nome': 'umohau',
    'telefone':'+258852702385',
    'email':'exemplo@gmail.com',
    'endereco': 'maputo,Moamba, Bairro exemplo',
    'BI':'100234567213A',
    'activo': False,
    'ADM': False
 }


def test_reactivate_operator_by_email_sucess(
        reactivate_operator_by_email,
        mock_audit,
        mock_auth,
        mock_message_box,
        mock_profile,
        mock_repo
    ):
    email= dto.email
    otp=dto.otp
    mock_repo.reactivate.return_value= 1
    mock_repo.search_email.return_value= operador
    res= reactivate_operator_by_email.execute(dto)
    output= res.unwrap()
    mock_auth.verificar_codigo.assert_called_once_with(otp)
    mock_repo.reactivate.assert_called_once_with(email)
    mock_repo.search_email.assert_called_once_with(email)
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)



def test_reativate_operator_by_email_permission_denied(
    reactivate_operator_by_email,
    mock_audit,
    mock_auth,
    mock_message_box,
    mock_profile,
    mock_repo
):
    type(mock_profile).ADM= PropertyMock(return_value=False)
    res= reactivate_operator_by_email.execute(dto)
    output= res.unwrap_err()
    mock_auth.verificar_codigo.assert_not_called()
    mock_repo.reactivate.assert_not_called()
    mock_repo.search_email.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value


def test_reactivate_operator_by_email_auth_failed(
    reactivate_operator_by_email,
    mock_audit,
    mock_auth,
    mock_message_box,
    mock_profile,
    mock_repo
):
    mock_auth.verificar_codigo.side_effect= InvalidOtpError
    res= reactivate_operator_by_email.execute(dto)
    output= res.unwrap_err()
    mock_repo.reactivate.assert_not_called()
    mock_repo.search_email.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.INCORRECT_OTP_ERROR.value


def test_reactivate_operator_by_email_repo_failed(
    reactivate_operator_by_email,
    mock_audit,
    mock_auth,
    mock_message_box,
    mock_profile,
    mock_repo
):
    otp=dto.otp
    mock_repo.reactivate.side_effect= EntityNotFoundError
    res= reactivate_operator_by_email.execute(dto)
    output= res.unwrap_err()
    mock_auth.verificar_codigo.assert_called_once_with(otp)
    mock_message_box.add_.assert_not_called()
    mock_repo.search_email.assert_not_called()
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()
    assert is_err(res)
    assert isinstance(output, OperatorError)
    assert output.value == OperatorError.OPERATOR_NOT_FOUND_ERROR.value
    


def test_reactivate_operator_by_email_message_box_fail(
    reactivate_operator_by_email,
    mock_audit,
    mock_auth,
    mock_message_box,
    mock_repo
) :
    email= dto.email
    otp= dto.otp
    mock_repo.reactivate.return_value= 1
    mock_repo.search_email.return_value= operador
    mock_message_box.add_.side_effect= OperationalError('error', (9), 'main')
    res= reactivate_operator_by_email.execute(dto)
    output= res.unwrap()
    mock_auth.verificar_codigo.assert_called_once_with(otp)
    mock_repo.reactivate.assert_called_with(email)
    mock_repo.search_email.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.MESSAGE_BOX_FAILLED.value in output.warnings


def test_reactivate_operator_by_email_audit_failed(
        reactivate_operator_by_email,
        mock_auth,
        mock_repo,
        mock_message_box,
        mock_audit
):
    email=dto.email
    otp=dto.otp
    mock_repo.reactivate.return_value= 1
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.search_email.return_value= operador
    res= reactivate_operator_by_email.execute(dto)
    output= res.unwrap()
    mock_auth.verificar_codigo.assert_called_once_with(otp)
    mock_repo.reactivate.assert_called_with(email)
    mock_repo.search_email.assert_called()
    mock_audit.auditar.assert_called()
    assert is_ok(res)
    assert isinstance(output, UpdateOutputDTO)
    assert BaseDomainError.AUDIT_FAILED.value in output.warnings
   