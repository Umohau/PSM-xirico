from __future__ import annotations
from typing import TYPE_CHECKING, List
from result import Result, Ok, Err, is_err, is_ok
import logging

from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from Projeto_xirico.exc import PermissionDeniedError, ProtectedEntityError, EntityNotFoundError, InvalidOtpError
from Projeto_xirico.domain_exceptions import BaseDomainError, OrderError
from Projeto_xirico.DTOs.baseDTO import UpdateOutputDTO
from Projeto_xirico.DTOs.orders_DTOS import OrderUpdateDTO

if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria, Autenticacao

logger= logging.getLogger(__name__)


class ChangeOrderMenager:
    def __init__(self,
        repo: OrdersRepository,
        profile: Profile,
        audit: Auditoria,
        message_box: messageBoxRepository,
        operator: OperatorRepository,
        auth: Autenticacao
    ):
        self._repo= repo
        self._profile= profile
        self._audit= audit
        self._message_box= message_box
        self._operator= operator
        self._auth= auth
        self._warninigs: List[BaseDomainError]= list()


    def _Change_menager(self, order_id, dados: dict):
        try:
            logger.debug('actualizando pedido %s', order_id)
            effect= self._repo.update(order_id= order_id, novos_dados= dados)
            logger.info('gestor do pedido: %s alterado com sucesso', order_id)
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except IntegrityError:
            logger.warning(
                'o id de novo gestor fornecido nao se encotra registrado no banco'
            )   
            return Err(BaseDomainError.INVALID_INPUT_DATA)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados ao tentar mudar o gestor do pedido', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(effect)


    def _get_order_details(self, order_id):
        try:
            logger.debug('recuperando os dados do pedido')
            order= self._repo.get_order_oid(order_id) #recupera os dados do pedido
            logger.debug(
                'dados recuperados'
            )
        except EntityNotFoundError:
            return Err(OrderError.ORDER_NOT_FOUND_ERROR)
        except OperationalError:
            logger.critical(
                'falha ao conectar com o banco de dados', exc_info=True
                )
            return Err(BaseDomainError.DB_CONECTION_ERROR)
        except DatabaseError:
            logger.error(
                'erro inesperado com o banco de dados', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(order)

    def _get_menagers_details(self, order_menager, new_menager_id):
        logger.debug(
            'recuperando dados dos gestores'
        )
        try:
            #recupera os emails do gestor actual e do novo gestor
            menager= self._operator.search_id(order_menager)
            new_menager= self._operator.search_id(new_menager_id)
            logger.info(
                'dados dos gestores recuperados com sucesso'
            )
        except DatabaseError:
            logger.warning(
                'erro inesperado ao recuperar dados dos gestores', exc_info=True
            )
            return Err(BaseDomainError.DB_ERROR)
        return Ok(
        {
            'old_menager_details': menager,
            'new_menager_details': new_menager
        }
        )


    def _auditar(self, order_id, operator_id, old_menager, new_menager):
        try:
            logger.debug('auditando a accao')
            self._audit.auditar(
                operador= operator_id,
                operacao= 'change_order_menager',
                detalhes= f'''alterou o gestor do pedido: {order_id}
                                de: {old_menager}
                                para: {new_menager}'''
            )
            logger.info(
                'operacao auditada com sucesso'
            )
        except Exception:
            logger.warning(
                'falha ao auditar a troca de gestor de um pedido'
            )
            self._warninigs.append(BaseDomainError.AUDIT_FAILED)

    def _push_notifications(self, old_menager: dict, new_menager: dict):
        logger.debug('enfileirando emails de notificacao para os gestores')
        try:
            self._message_box.add_(
                dados={
                    'to': old_menager.get('email'),
                    'type': 'old_menager',
                    'name': old_menager.get('nome'),
                    'channel': 'email',

                }
            )
            logger.info(
                'email enfileirado para o gestor antigo'
            )

            self._message_box.add_(
                dados={
                    'to': new_menager.get('email'),
                    'type': 'new_menager',
                    'name': new_menager.get('nome'),
                    'channel': 'email'
                }
            )
            logger.info(
                'email enfileirado para o novo gestor'
            )
        except DatabaseError:
            logger.warning('falha no enfileiramento dos emails para os gestores', exc_info=True)
            self._warninigs.append(BaseDomainError.MESSAGE_BOX_FAILLED)


    def execute(self, dados:OrderUpdateDTO ) -> Result[UpdateOutputDTO, BaseDomainError| OrderError]:
        logger.debug('iniciando operacao de troca de gestor do pedido %s', dados.order_id)

        #recupera os dados do pedido
        order_= self._get_order_details(order_id=dados.order_id)
        if is_err(order_):
            return order_
        order= order_.unwrap()
        order_menager= order.get("gestor_id") #recupera o id do gestor do pedido
        operator_id= self._profile.id #guarda o id do operador logado
        order_status= order.get('estado') #guarda o estado do pedido

        #recupera os dados dos gestores
        details_= self._get_menagers_details(
            order_menager= order_menager,
            new_menager_id= dados.menager_id)
        if is_err(details_):
            return details_
        details= details_.unwrap()
        new_menager_details= details.get('new_menager_details')
        old_menager_details= details.get('old_menager_details')

        # monta os dados de actualizacao
        new_menager= {'gestor_id': dados.menager_id}
        
        #verifica a permissao para liberar edicao do pedido
        logger.debug('verificando permicao')
        if not order_menager == operator_id and not self._profile.ADM:
            logger.warnig('permissao negada ao operador: %s para trocar o gestor do pedido %s',operator_id, dados.order_id)
            return Err(BaseDomainError.PERMISSION_DENIED_ERROR)

        # confirma a identidade do novo gestor
        try:
            logger.debug('confirmando identidade do novo gestor por 2FA')
            self._auth.verificar_otp(dados.otp)
            logger.info(
                'identidade confirmada em 2FA'
            )
        except InvalidOtpError:
            logger.info('codigo otp incorrecto')
            return Err(BaseDomainError.INCORRECT_OTP_ERROR)
        except Exception as e:
            logger.warning('codigo otp invalido err:%s', str(e))
            return Err(BaseDomainError.INVALID_OTP_ERROR)
        
        #verifica o estado do pedido para liberar a edicao
        logger.debug('verificando estado do pedido')
        if not order_status=='pendente': 
            logger.warnig(
                'entidate protegida, accao barada ao operador: %s somente pedidos pendentes podem ser editados, status: %s',
                operator_id, order_status
                )
            return Err(BaseDomainError.PROTETECD_ENTITY_ERROR)

        #altera o gestor no banco de dados
        logger.debug(
            'alterando gestor do pedido'
        )
        effect_= self._Change_menager(dados.order_id, dados= new_menager)
        if is_err(effect_):
            return effect_
        effect= effect_.unwrap()

        #registra a accao em log de auditoria
        self._auditar()

        #enfileira uma notificacao para o gestor anterior e o novo gestor
        self._push_notifications(
            old_menager=old_menager_details,
            new_menager= new_menager_details
        )

        logger.debug('operacao de actualizacao concluida com sucesso')
        return Ok(
            UpdateOutputDTO(
                warnings= self._warninigs, 
                new_data= str(dados.menager_id),
                old_data= str(order_menager),
                effect= effect,
                updated_id= dados.order_id
            )
        )
