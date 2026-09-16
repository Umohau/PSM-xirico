from pydantic import BaseModel, Field
from typing import Annotated, Optional, List

WARNINGS= Annotated[
    List[str],
    Field(
        title='warnings',
        description='avisos que ocorem durante a operacao',
        default_factory=List
    )]


class UpdateOutputDTO(BaseModel):
    warnings: WARNINGS
    updated_id: Optional[int|str]= Field(
        title='updated id',
        description='id alvo do update'
    )
    effect: int=Field(
        title= 'effect',
        description= 'effexted rows on update',
        examples=['effect=1']
    )
    new_data: str=Field(
        title= 'new data',
        description= 'novo dado inserido',
    )
    old_data: str= Field(
        title='old data',
        description='dado antigo o que foi substituido pelo novo'
    )


class InsertOutputDTO(BaseModel):
    warnings: WARNINGS
    genereted_id: Optional[int|str]=Field(
        title='genereted_id',
        description='id gerado durante a insersao',
        examples=[1, '1']
    )

