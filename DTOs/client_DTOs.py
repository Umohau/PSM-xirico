from pydantic import BaseModel, Field, EmailStr
from typing import  Annotated, Optional
from pydantic_extra_types.phone_numbers import PhoneNumber

# Tipos reutilizaveis com Annotated

ID= Annotated[
    int,
    Field(
        title='id',
        description='id de registro do cliente',
        examples=['id=1']
    )
    ]

NAME= Annotated[
    str,
    Field(
        min_length=3,
        title='nome',
        description='nome completo do cliente',
        examples=['name= Umohau']
    )
]

EMAIL= Annotated[
    EmailStr,
    Field(
        title='email',
        description='email valido do cliente',
        examples=['cliente@gmail.com']
    )
]

DOMAIN= Annotated[
    str,
    Field(
        min_length=8,
        title= 'domain',
        description='dominio do cliente',
        examples='muhau bird shop tai'
    )
]

TELEPHONE= Annotated[
    PhoneNumber,
    Field(
        title='telephone',
        description='telefone valido do cliente',
        examples= '+258 867073879'
    )
]


ADRESSES= Annotated[
    str,
    Field(
        title= 'endereco',
        desciption= 'endereco fisico do operador',
        examples='Maputo, praca dos herois avenida 25, Q21',
        min_length= 15,

    )
]


class ClientGetResponseDTO(BaseModel):
    client_id: ID
    name: NAME
    email: EMAIL
    domain: Optional[DOMAIN]=None
    telephone: TELEPHONE
    address: ADRESSES


class ClientRegistDTO(BaseModel):
    name: NAME
    email: EMAIL
    domain: Optional[DOMAIN]=None
    telephone: TELEPHONE
    address: ADRESSES


class ClientUpdateDTO(BaseModel):
    client_id: ID
    name: Optional[NAME]= None
    email: Optional[EMAIL]= None
    domain: Optional[DOMAIN]=None
    telephone: Optional[TELEPHONE]= None
    address: Optional[ADRESSES]= None
