import pytest
from datetime import datetime, timezone
from result import is_ok, is_err
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.DTOs.shipment_DTO import ShipmentGetResponseDTO
from Projeto_xirico.domain_exceptions import BaseDomainError, ShipmentsError
from Projeto_xirico.use_cases.orders_use_cases.search_shipmants import SearchShipmentByOrderId, SearchShipmentsByEpoc
from Projeto_xirico.exc import EntityNotFoundError


data_inicio= datetime.now(timezone.utc).date()
data_fim=  datetime.now(timezone.utc).date()


@pytest.fixture
def search_shipments_by_order_id(mock_repo):
    return SearchShipmentByOrderId(repo= mock_repo)


@pytest.fixture
def search_shipments_by_epoc(mock_repo):
    return SearchShipmentsByEpoc(repo= mock_repo)


@pytest.fixture
def dados(tmp_path):
    open(tmp_path/'teste.pdf', 'x')
    with open(tmp_path/'teste.pdf', 'rb') as arquivo:
        docs= arquivo.read()
        return {
            'exportacao_id':2,
            'order_id': 'ORD1234',
            'processo_docs': docs
        }



@pytest.fixture
def dados2(tmp_path):
    open(tmp_path/'teste.pdf', 'x')
    with open(tmp_path/'teste.pdf', 'rb') as arquivo:
        docs= arquivo.read()
        return[ {
            'exportacao_id':2,
            'order_id': 'ORD1234',
            'processo_docs': docs
        }]


def test_search_shepments_by_order_id_sucess(dados, mock_repo, search_shipments_by_order_id):
    mock_repo.get_shipment_oid.return_value= dados
    res= search_shipments_by_order_id.execute('ORD123')
    mock_repo.get_shipment_oid.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, ShipmentGetResponseDTO)


def test_search_shipment_by_order_id_shipment_not_found(mock_repo, search_shipments_by_order_id):
    mock_repo.get_shipment_oid.side_effect= EntityNotFoundError
    res= search_shipments_by_order_id.execute('ORD123')
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, ShipmentsError)
    assert output.value == ShipmentsError.SHIPMENT_NOT_FOUND_ERROR.value

def test_search_shipment_by_order_id_db_conection_error(mock_repo, search_shipments_by_order_id):
    mock_repo.get_shipment_oid.side_effect= OperationalError('error', (9), 'main')
    res= search_shipments_by_order_id.execute('ORD123')
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value



def test_search_shipment_by_order_id_db_error(mock_repo, search_shipments_by_order_id):
    mock_repo.get_shipment_oid.side_effect= DatabaseError('error', (9), 'main')
    res= search_shipments_by_order_id.execute('ORD123')
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value


def test_search_shipments_by_epoc_sucess(dados2, mock_repo, search_shipments_by_epoc):
    mock_repo.search_epoc.return_value= dados2
    res= search_shipments_by_epoc.execute(data_inicio= data_inicio, data_limite= data_fim)
    mock_repo.search_epoc.assert_called()
    assert is_ok(res)
    output= res.unwrap()
    assert isinstance(output, list)
    assert isinstance(output[0], ShipmentGetResponseDTO)


def test_search_shipment_by_epoc_shipment_not_found(mock_repo, search_shipments_by_epoc):
    mock_repo.search_epoc.side_effect= EntityNotFoundError
    res= search_shipments_by_epoc.execute(data_inicio= data_inicio, data_limite= data_fim)
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, ShipmentsError)
    assert output.value == ShipmentsError.SHIPMENT_NOT_FOUND_ERROR.value


def test_search_shipment_by_epoc_db_conection_error(mock_repo, search_shipments_by_epoc):
    mock_repo.search_epoc.side_effect= OperationalError('error', (9), 'main')
    res= search_shipments_by_epoc.execute(data_inicio= data_inicio, data_limite= data_fim)
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_CONECTION_ERROR.value


def test_search_shipment_by_epoc_db_error(mock_repo, search_shipments_by_epoc):
    mock_repo.search_epoc.side_effect= DatabaseError('error', (9), 'main')
    res= search_shipments_by_epoc.execute(data_inicio= data_inicio, data_limite= data_fim)
    assert is_err(res)
    output= res.unwrap_err()
    assert isinstance(output, BaseDomainError)
    assert output.value == BaseDomainError.DB_ERROR.value
    