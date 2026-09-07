from __future__ import annotations
from typing import TYPE_CHECKING
from result import Result, Ok,Err
import logging

from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError
from Projeto_xirico.domain_exceptions import BaseDomainError
from Projeto_xirico.DTOs.baseDTO import InsertOutputDTO
from Projeto_xirico.DTOs.orders_DTOS import OrderRegistDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class AddNewOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= Profile
        self._audit= audit


    def execute(self, dados: OrderRegistDTO) -> Result[InsertOutputDTO, BaseDomainError]:
        logger.debug(
            'iniciando registro de pedido'
        )
        dados_={
            "cliente_id":dados.client_id,
            "gestor_id": dados.menager_id,
            "ave_id":dados.bird,
            "quantidade": dados.quantity,
        }
        Warnings: list[BaseDomainError]= list()

        try:
            logger.debug(
                'persistindo os dados do pedido'
            )
            id_gerado= self._repo.insert(dados)
            logger.info(
                'pedido inserido com sucesso'
            )
        except IntegrityError:
            logger.warning(
                'dados de entrada invalidos, ou chaves estrangeiras violadas', exc_info= True
            )
            return Err(BaseDomainError.INVALID_INPUT_DATA)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco para registrar um pedido', exc_info=True
            )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)

        try:
            logger.debug(
                'auditando operacao de registro de pedido'
            )
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'add_new_order',
                detalhes= f'adicionou o pedido id: {id_gerado}'
            )
            logger.info(
                'operacao de registro de pedido auditado com sucesso'
            )
        except Exception:
            logger.warning(
                'falha inesperada ao registrar aiditoria do registro do pedido %s', id_gerado, exc_info=True
            )
            Warnings.append(BaseDomainError.AUDIT_FAILED)

        return Ok(
            InsertOutputDTO(
                warnings= Warnings,
                genereted_id= id_gerado
            )
        )



   