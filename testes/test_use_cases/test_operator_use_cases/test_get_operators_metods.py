import pytest
from unittest.mock import PropertyMock
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError

from Projeto_xirico.DTOs.operator_DTOs import OperatorGetByAdmResponseDTO, OperatorGetResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, OperatorError
from Projeto_xirico.use_cases.operator_use_cases.get_inactive_operators import GetInactiveOperators
from Projeto_xirico.use_cases.operator_use_cases.list_active_operators import ListActiveOperators
from Projeto_xirico.use_cases.operator_use_cases.search_by_id import SearchByID
from Projeto_xirico.use_cases.operator_use_cases.search_by_name import SearchByName


@pytest.fixture
def get_inactive_operators(
    mock_repo,
    mock_profile
):
    return GetInactiveOperators(
        repo= mock_repo,
        profile= mock_profile
    )


@pytest.fixture
def list_active_operators(mock_repo, mock_profile, mock_audit):
    return ListActiveOperators(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


@pytest.fixture
def search_by_id(
    mock_repo,
    mock_profile,
    mock_audit):
    return SearchByID(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


@pytest.fixture
def search_by_name(mock_repo, mock_profile, mock_audit):
    return SearchByName(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


dados={
    'id':1,
    'nome': 'umohau',
    'telefone':'+258852702385',
    'email':'exemplo@gmail.com',
    'endereco': 'maputo,Moamba, Bairro exemplo',
    'identificacao':'100234567213A',
    'activo': False,
    'ADM': False
 }

def test_get_inactive_operator_OPR_sucess(
        get_inactive_operators,
        mock_repo,
        mock_audit
        ):
    mock_repo.get_inactives.return_value= [dados]
    res= get_inactive_operators.execute()
    output=res.unwrap()
    mock_repo.get_inactives.assert_called_once()
    assert is_ok(res)
    assert isinstance(output[0], OperatorGetByAdmResponseDTO)
    assert output[0].roll == 'OPR'



def test_get_inactive_operator_ADM_sucess(
        get_inactive_operators,
        mock_repo,
        mock_audit
        ):
    dados_= dados.copy()
    dados_['ADM']= True
    mock_repo.get_inactives.return_value= [dados_]
    res= get_inactive_operators.execute()
    output=res.unwrap()
    mock_repo.get_inactives.assert_called_once()
    assert is_ok(res)
    assert isinstance(output[0], OperatorGetByAdmResponseDTO)
    assert output[0].roll == 'ADM'

def test_get_inactives_operators_DB_conexion_error(
    get_inactive_operators,
    mock_repo
):
    mock_repo.get_inactives.side_effect= OperationalError('error', (9),'main')
    res= get_inactive_operators.execute()
    output= res.unwrap_err()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value

def test_get_inactives_operators_eperators_not_found(
    get_inactive_operators,
    mock_repo
):
    mock_repo.get_inactives.return_value= []
    res= get_inactive_operators.execute()
    output= res.unwrap_err()
    assert is_err(res)
    assert isinstance(output, OperatorError)
    assert output.value == OperatorError.OPERATOR_NOT_FOUND_ERROR.value


def test_list_active_operators_DTO_ADM(
    list_active_operators,
    mock_repo
):
    mock_repo.search_all.return_value= [dados]
    res= list_active_operators.execute()
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, list)
    assert isinstance(output[0], OperatorGetByAdmResponseDTO)


def test_list_active_operators_DTO_OPR(
    list_active_operators,
    mock_repo,
    mock_profile
):
    type(mock_profile).ADM= PropertyMock(return_value= False)
    mock_repo.search_all.return_value= [dados]
    res= list_active_operators.execute()
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, list)
    assert isinstance(output[0], OperatorGetResponseDTO)



def test_list_active_operators_roll_OPR(
    list_active_operators,
    mock_repo,
):
    dados_= dados.copy()
    dados_['ADM']= False
    mock_repo.search_all.return_value= [dados_]
    res= list_active_operators.execute()
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, list)
    assert output[0].roll == 'OPR'



def test_list_active_operators_roll_ADM(
    list_active_operators,
    mock_repo
):
    dados_= dados.copy()
    dados_['ADM']= True
    mock_repo.search_all.return_value= [dados_]
    res= list_active_operators.execute()
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, list)
    assert output[0].roll == 'ADM'


def test_list_active_operators_DB_conexion_error(
    list_active_operators,
    mock_repo
):
    mock_repo.search_all.side_effect= OperationalError('erro', (9), 'main')
    res= list_active_operators.execute()
    output= res.unwrap_err()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_search_by_id_DTO_ADM(
    search_by_id,
    mock_repo
):
    mock_repo.search_id.return_value= dados
    res= search_by_id.execute(1)
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, OperatorGetByAdmResponseDTO)


def test_search_by_id_permission_denied(
    search_by_id,
    mock_repo,
    mock_profile
        ):
    type(mock_profile).ADM= PropertyMock(return_value= False)
    res= search_by_id.execute(1)
    output= res.unwrap_err()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.PERMISSION_DENIED_ERROR.value
    

def test_search_by_id_roll_ADM(
    search_by_id,
    mock_repo
    ):
    dados_= dados.copy()
    dados_['ADM']= True
    mock_repo.search_id.return_value= dados_
    res= search_by_id.execute(1)
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, OperatorGetByAdmResponseDTO)
    assert output.roll == 'ADM'


def test_search_by_id_roll_OPR(
    search_by_id,
    mock_repo
    ):
    dados_= dados.copy()
    dados_['ADM']= False
    mock_repo.search_id.return_value= dados_
    res= search_by_id.execute(1)
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, OperatorGetByAdmResponseDTO)
    assert output.roll == 'OPR'
    

def test_search_name_DTO_ADM(
    search_by_id,
    mock_repo,
    search_by_name
):
    mock_repo.search_name.return_value= [dados]
    res= search_by_name.execute('teste')
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, list)
    assert isinstance(output[0], OperatorGetByAdmResponseDTO)



def test_search_by_name_roll_OPR(
    search_by_name,
    mock_repo,
):
    dados_= dados.copy()
    dados_['ADM']= False
    mock_repo.search_name.return_value= [dados_]
    res= search_by_name.execute('teste')
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, list)
    assert output[0].roll == 'OPR'



def test_search_by_name_DTO_OPR(
    search_by_name,
    mock_repo,
    mock_profile
):
    type(mock_profile).ADM= PropertyMock(return_value= False)
    mock_repo.search_name.return_value= [dados]
    res= search_by_name.execute('teste')
    output= res.unwrap()
    assert is_ok(res)
    assert isinstance(output, list)
    assert isinstance(output[0], OperatorGetResponseDTO)



def test_search_by_name_DB_conexion_error(
    search_by_name,
    mock_repo
):
    mock_repo.search_name.side_effect= OperationalError('erro', (9), 'main')
    res= search_by_name.execute('teste')
    output= res.unwrap_err()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value
