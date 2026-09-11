import pytest
from datetime import datetime
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError,DatabaseError
from Projeto_xirico.domain_exceptions import BaseDomainError, ShipmentsError
from Projeto_xirico.exc import EntityNotFoundError
from Projeto_xirico.DTOs.shipment_DTO import ShipmentGetResponseDTO
from Projeto_xirico.use_cases.client_use_cases.list_client_shipments import ListClientShipments

@pytest.fixture
def list_client_shipments(mock_repo):
    return ListClientShipments(mock_repo)



@pytest.fixture
def dados(tmp_path):
    open(tmp_path/'teste.pdf', 'x')
    with open(tmp_path/'teste.pdf', 'rb') as arquivo:
        docs= arquivo.read()
        return {
            'process_docs': docs,
            'exportacao_id': 1,
            'order_id': 'ORD123'
        }


def test_list_client_shipmetns_sucess(mock_repo, list_client_shipments, dados):
    mock_repo.get_shipments_cl.return_value= [dados]
    res= list_client_shipments.execute(1)
    output= res.unwrap()
    mock_repo.get_shipments_cl.assert_called_once()
    assert is_ok(res)
    assert isinstance(output, list)
    assert isinstance(output[0],ShipmentGetResponseDTO )


def test_list_client_shipmetns_shipments_not_found_error(
    mock_repo,
    list_client_shipments
):
    id=1
    mock_repo.get_shipments_cl.side_effect= EntityNotFoundError
    res= list_client_shipments.execute(1)
    output= res.unwrap_err()
    mock_repo.get_shipments_cl.assert_called_once()
    assert is_err(res)
    assert isinstance(output, ShipmentsError)
    assert output.value == ShipmentsError.SHIPMENT_NOT_FOUND_ERROR.value



def test_list_client_shipmetns_db_conection_error(
    mock_repo,
    list_client_shipments
    
):
    id=1
    mock_repo.get_shipments_cl.side_effect= OperationalError('erro', (9), 'main')
    res= list_client_shipments.execute(id)
    output= res.unwrap_err()
    mock_repo.get_shipments_cl.assert_called_once()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value



def test_list_client_shipmetns_db_error(
    mock_repo,
    list_client_shipments
):
    mock_repo.get_shipments_cl.side_effect= DatabaseError('erro', (9), 'main')
    res= list_client_shipments.execute(1)
    output= res.unwrap_err()
    mock_repo.get_shipments_cl.assert_called_once()
    assert is_err(res)
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value