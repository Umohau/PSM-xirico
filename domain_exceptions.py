from enum import Enum

class BaseDomainError(Enum):
    AUDIT_FAILED= "falha no registro de auditoria"
    MESSAGE_BOX_FAILLED= "falha ao enfileirar a notificacao"
    EMPTY_TABLE='falha ao buscar dados sua tabela esta vazia'
    DB_ERROR= 'erro no banco de dados'
    DB_CONECTION_ERROR= 'falha ao conectar com o banco de dados'


class BirdsError(Enum):
    BIRD_ALREAD_EXISTS= "Ave ja existente no catalogo"
    BIRD_NOT_FOUND="ave nao encontrada no catalogo"


class OperatorError(Enum):
    OPERATOR_ALREAD_EXISTS= "O Operador ja se encontra cadastrado"
    OPERATOR_DUPLICATE_EMAIL= "ja existe um poerador ja cadastrado com o email fornecido"
