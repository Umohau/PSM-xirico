from pydantic import BaseModel, Field
from typing import Optional, List
from typing import Annotated


#tipos para birds DTOs
COMUN_NAME=Annotated[
    str,
    Field(
        title='usual_name',
        description='nome comum osual  da ave',
        examples='xiricos',
        min_length=5
    )]


CIENTIFIC_NAME=Annotated[
    str,
    Field(
        title='cientific_name',
        description='nome cientifico da ave',
        examples='Crithagra mozambicus',
        min_length=4
    )]


SPECIES=Annotated[
    str,
    Field(
        title='especie',
        description='especie da ave',
        alias='bird_species',
        min_length=2
        )]


PRICE=Annotated[
    int,
    Field(
        title='price',
        description='preco da ave em dolares',
        alias= 'bird_price',
        examples='15',
        ge=0
        )]


STATUS= Annotated[
    str,
    Field(
        title='status',
        description= 'disponobilidade da ave no catalogo',
        examples=['disponivel', 'indisponivel'],
        default='Disponivel'
        )]


BIRD_ID= Annotated[
    int,
    Field( 
        title='bird id',
        description='id de registro da ave',
        examples='123',
        alias='bird_id',
        
    )]


WARNINGS= Annotated[
    List[str],
    Field(
        title='warnings',
        description='avisos que ocorem durante a operacao',
        default_factory=List
    )]


#DTOs para birds
class BirdGetResponseDTO(BaseModel):
    bird_id: BIRD_ID
    usual_name: COMUN_NAME
    cientific_name: CIENTIFIC_NAME 
    species: SPECIES
    price: PRICE
    status: STATUS


class BirdsAddDTO(BaseModel):
    usual_name: COMUN_NAME
    cientific_name: CIENTIFIC_NAME
    species: SPECIES
    price: PRICE


class BirdsUpdateDTO(BaseModel):
    bird_id: BIRD_ID
    usual_name:Optional[COMUN_NAME]=None
    cientific_name:Optional[CIENTIFIC_NAME]=None
    species:Optional[SPECIES]= None
    price:Optional[PRICE]= None


class AddBirdOutPutDTO(BaseModel):
    id_gerado: BIRD_ID
    warnings: WARNINGS
