from pydantic import BaseModel, Field
from typing import Optional, List
from typing import Annotated


class ShipmentGetResponseDTO(BaseModel):
    order_id: str
    shipment_id:int
    process_docs: bytes


class RegistShipmentDTO(BaseModel):
    order_id: str
    process_docs: bytes