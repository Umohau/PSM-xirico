from enum import Enum

class BaseDomainError(Enum):
    AUDIT_FAILED= "falha no registro de auditoria"
    MESSAGE_BOX_FAILLED= "falha ao enfileirar a notificacao"
    EMPTY_TABLE='falha ao buscar dados sua tabela esta vazia'
    DB_ERROR= 'erro no banco de dados'
    DB_CONECTION_ERROR= 'falha ao conectar com o banco de dados'
    PERMISSION_DENIED_ERROR= 'nao tem permissao para executar esta accao'
    INVALID_OTP_ERROR= 'codogo otp invalido'
    ATTEMPTS_EXCEDED_ERROR= 'atingiu o limite de tentativas'
    INCORRECT_OTP_ERROR= 'codigo otp incorrecto'

class BirdsError(Enum):
    BIRD_ALREAD_EXISTS= "Ave ja existente no catalogo"
    BIRD_NOT_FOUND="ave nao encontrada no catalogo"


class OperatorError(Enum):
    OPERATOR_ALREAD_EXISTS_ERROR= "O Operador ja se encontra cadastrado"
    OPERATOR_NOT_FOUND_ERROR= 'operador nao encontrado'
    OPERATOR_DUPLICATE_EMAIL_ERROR= "o email fornecido ja se encontra cadastrado"
    OPERATOR_DUPLICATE_TELEFONE_ERROR= 'o numero telefonico ja se encontra cadastrado'
    OPERATOR_DUPLICATE_BI_ERROR= 'o BI fornecido ja se encontra cadastrado'


class ShipmentsError(Enum):
    SHIPMENT_NOT_FOUND_ERROR= 'nao foram encontradas exportacoes correspondentes'


class OrderError(Enum):
    ORDER_NOT_FOUND_ERROR= 'nao foram encontrados pedidos correspondentes'