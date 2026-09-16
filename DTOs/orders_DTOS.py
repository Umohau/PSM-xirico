from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import date

# tipos
ORDER_ID= Annotated[
    str,
    Field(
        title='order id',
        description="id do pedido, texto que comeca com 'ORD'",
        examples='ORD123',
        alias='id'
    )
]

DATE= Annotated[
    date,
    Field(
        title='date of regist',
        description= 'data de registro do pedido',
        examples=['2026/05/15']
    )
]

BIRD= Annotated[
    int,
    Field(
        title= 'bird id',
        description= 'id de registro da ave',
        examples=12
    )
]

STATUS= Annotated[
    str, 
    Field(
        min_length=4,
        max_length=8,
        title='status',
        description='estado do pedido',
        examples=['status= Pending']
    )
]

class OrderGetResponseDTO(BaseModel):
    order_id: ORDER_ID
    date_of_regist: DATE
    sent_date: Optional[DATE]= None
    menager_id: int
    client_id: int
    quantity: int
    bird: BIRD
    order_status: STATUS

class OrderRegistDTO(BaseModel):
    date_of_regist: DATE
    menager_id: int
    client_id: int
    quantity: int
    bird: BIRD


class OrderUpdateDTO(BaseModel):
    order_id: ORDER_ID
    otp: Optional[str]=None
    date_of_regist: Optional[DATE]= None
    sent_date: Optional[DATE]= None
    menager_id: Optional[int]= None
    client_id: Optional[int]= None
    quantity: Optional[int]=None
    bird: Optional[BIRD]=None
    order_status: Optional[STATUS]= None