from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Optional
from pydantic_extra_types.phone_numbers import PhoneNumber


#tipos personalizados
OPERATOR_ID= Annotated[
    int,
    Field(
        title= 'operator_id',
        description= 'ID de registro do operador',\
        examples=1,
        alias= 'operator_id'
    )]

EMAIL= Annotated[
    EmailStr,
    Field(
        title= 'email do operador',
        description= 'email valido do operador',
        examples='exemplo@gmail.com',
        alias= 'operator_email'
    )]


OPERATOR_NAME= Annotated[
    str,
    Field(
        title= 'nome do operdor',
        description= 'nome completo do operador',
        examples= 'Ricardo Pedro Kossa',
        min_length=3,
        alias= 'operator_name'
    )
]


TELEPHONE= Annotated[
    PhoneNumber,
    Field(
        title='telefone',
        description= 'numero telefonico do operador',
        examples='+258 852703286',
        alias= 'phone_number'
    )
]


ADRESSES= Annotated[
    str,
    Field(
        title= 'endereco',
        desciption= 'endereco fisico do operador',
        examples='Maputo, praca dos herois avenida 25, Q21',
        min_length= 15,
        alias= 'morada'
    )
]


OPERATOR_ROLE= Annotated[
    str,
    Field(
        title= 'operator role',
        description= 'cargo do operador (ADM ou OPR)' \
        'ADM: Administrador,' \
        'OPR: Operador comum',
        examples=['ADM', 'OPR'],
        max_length=3,
        min_length=3,
    )
]


OPERATOR_STATUS=  Annotated[
    str,
    Field(
        title='estado',
        description='estado do operador',
        max_length= 11,
        min_length= 6,
        default= 'Activo',
        examples=['activo' , 'desactivado']
    )
]


OPERATOR_PERSONAL_ID= Annotated[
    str,
    Field(
        title='bilhete de identidade',
        desciption= 'bilhete de identidade pessoal do operador(BI)',
        pattern=r'^[0-9]{12}[A-Z]$',
        alias= 'BI',
        examples='100231239823A'
    )
]


OTP= Annotated[
    str,
    Field(
        title='otp',
        description='codigo otp enviado ao oprador para registro',
        min_length=8,
        max_length=8,
        alias= 'codigo',
        serialization_alias='otp'
    )
]


class OperatorGetResponseDTO(BaseModel):
    id: OPERATOR_ID
    name: OPERATOR_NAME
    roll: OPERATOR_ROLE
    status: OPERATOR_STATUS

    
class OperatorGetByAdmResponseDTO(BaseModel):
    id: OPERATOR_ID
    name: OPERATOR_NAME
    roll: OPERATOR_ROLE
    email: EMAIL
    telephone: TELEPHONE
    adress: ADRESSES
    BI: OPERATOR_PERSONAL_ID
    status: OPERATOR_STATUS


class OperatoraUpdateDTO(BaseModel):
    id: Optional[OPERATOR_ID]= None
    name: Optional[OPERATOR_NAME]= None
    roll: Optional[OPERATOR_ROLE]=None
    email: Optional[EMAIL]= None
    telephone: Optional[TELEPHONE]= None
    adress: Optional[ADRESSES]= None
    BI: Optional[OPERATOR_PERSONAL_ID]= None
    status: Optional[OPERATOR_STATUS]= None


class RegistOperatorDTO(BaseModel):
    name: OPERATOR_NAME
    email: EMAIL
    telephone: TELEPHONE
    adress: ADRESSES
    BI: OPERATOR_PERSONAL_ID
    otp:OTP


class ReactivateOperatorDTO(BaseModel):
    email: EmailStr
    otp: OTP