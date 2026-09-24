from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Optional, List
from pydantic_extra_types.phone_numbers import PhoneNumber
from Projeto_xirico.seguranca import GestorDeSessao


class EnterUserDataDTO(BaseModel):
    user_password: str
    user_email: EmailStr


class LoginOutput(BaseModel):
    session: object
    warnings:List