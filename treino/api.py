from ninja import Router
from .schemas import AlunosSchema, ProgressoAlunoSchema, AulasRealizadasSchema
from .models import Alunos, AulasConcluidas
from ninja.errors import HttpError
from typing import List
from .progresso import *
from datetime import date

treino_router = Router()


'''status da resposta http (statuscode) 
    200 = sucesso
    400 = usuario fez algo errado
    500 = erro interno no servidor 
'''
@treino_router.post('', response={200:AlunosSchema})
def criar_aluno(request, aluno_schema: AlunosSchema):
    nome = aluno_schema.dict()['nome']
    email = aluno_schema.dict()['email']
    faixa = aluno_schema.dict()['faixa']
    data_nascimento = aluno_schema.dict()['data_nascimento']

    ''' "descomprensão de dados":
    nome, email, faixa, data_nascimento = **aluno_schema.dict()
        OU APENAS
    aluno = Alunos(**aluno_schema.dict())
    '''
    #exists()=> se tem alguem com esse email, retorna true, se não, false
    if Alunos.objects.filter(email=email).exists():
        raise HttpError(400, "Este e-mail já foi cadastrado!")

    aluno = Alunos(nome=nome, email=email,faixa=faixa,data_nascimento=data_nascimento)
    aluno.save()

    return aluno


@treino_router.get('/alunos/', response=List[AlunosSchema]) #informando a forma que vamos receber a resposta POIS alunos retorna mais de um valor
def listar_alunos(request):
    alunos = Alunos.objects.all()
    return alunos


@treino_router.get('/progresso_aluno/', response={200: ProgressoAlunoSchema})
def progresso_aluno(request, email_aluno:str):
    aluno = Alunos.objects.get(email=email_aluno)
    faixa_atual = aluno.get_faixa_display() #pega o texto ao invés da letra
    num_faixa = dic_faixas.get(faixa_atual, 0)

    total_aulas_prox_faixa = calcular_classes_upgrade(num_faixa)

    aulas_concluidas_faixa =  AulasConcluidas.objects.filter(aluno=aluno, faixa_atual=aluno.faixa).count()
    aulas_faltantes = total_aulas_prox_faixa - aulas_concluidas_faixa

    return {
        "email": email_aluno,
        "nome": aluno.nome,
        "faixa": faixa_atual,
        "total_aulas": aulas_concluidas_faixa,
        "aulas_faltantes_pra_prox_faixa": aulas_faltantes
    }

@treino_router.post('/aula_realizada/', response={200:str})
def aula_realizada(request, aula_realizada=AulasRealizadasSchema):
    
    qtd = aula_realizada.dict()['qtd']
    email_aluno = aula_realizada.dict()['email_aluno']
    
    if qtd <=0:
        raise HttpError(400, 'Quantidade inválida de aulas. Quantidade deve ser maior que zero!')

    aluno= Alunos.objects.get(email=email_aluno)

    for _ in range(0, qtd):
        ac = AulasConcluidas(
            aluno = aluno,
            faixa_atual= aluno.faixa
        )
        ac.save()
    ''' versao avançada (mais eficiente)
    aulas = [
        AulasConcluidas(aluno=aluno, faixa_atual=aluno.faixa)
        for _ in range(qtd)
    ]
    AulasConcluidas.objects.bulk_create(aulas) 
    
        bulk create-> gera todos os dados em  um unico sql
    '''
    return 200, f"Aula marcada como realizada para o aluno {aluno.nome}"



@treino_router.put('/alunos/{aluno_id}', response=AlunosSchema)
def update_aluno(request, aluno_id:int, aluno_data: AlunosSchema):
    aluno =Alunos.objects.get(id=aluno_id)
    idade = date.today() - aluno.data_nascimento

    if int(idade.days/365) < 18 and aluno_data.ditc()['faixa'] in ('A','R','M','P'):
        raise HttpError(400, "Menores de 18 não podem receber esta faixa")

    '''forma bruta:
        aluno.nome = aluno_data.dict()['nome']
        aluno.email = aluno_data.dict()['email']
        aluno.faixa = aluno_data.dict()['faixa']
    '''
    #exclude_unset=True
    for attr, value in aluno_data.dict().items():
        if value:
            #ps: deu erro na data, qria colocar algo tipo value != do value q ja tem no atributo, mas nao sei como
            setattr(aluno, attr, value) # "nesta class, altere este atributo, para este valor"
    aluno.save()
    return aluno
