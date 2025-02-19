from ninja import ModelSchema, Schema 
'''
    modelschema: cria a representação baseado em uma determinada model;
    schema: cria do zero uma representação dos dados que sao retornados ou recebidos pelo endpoint 
'''

from .models import Alunos
from typing import Optional

class AlunosSchema(ModelSchema):
    class Meta:
        model = Alunos
        fields = ['nome', 'email', 'faixa', 'data_nascimento']

class ProgressoAlunoSchema(Schema):
    email:str
    nome:str
    faixa:str
    total_aulas: int
    aulas_faltantes_pra_prox_faixa:int

class AulasRealizadasSchema(Schema):
    qtd: Optional[int] = 1
    email_aluno: str