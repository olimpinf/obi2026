####################
# SERPRO
####################
SERPRO_KEY='cosEyqffhaRsemSx8bp8GFc6lWMa'
SERPRO_SECRET='VOq8yYjRpBXqMnGRcB3SU7Qw6EEa'
URL_TOKEN='https://gateway.apiserpro.serpro.gov.br/token'
URL_CONSULTA='https://gateway.apiserpro.serpro.gov.br/consulta-cpf-df/v1/cpf/'


import base64
import json
import requests
import re
import unidecode
from obi.settings import DEBUG

token = ''

def generate_bearer_token():
    credential = base64.b64encode(f"{SERPRO_KEY}:{SERPRO_SECRET}".encode("utf8")).decode("utf8")
    
    headers = {
        "Authorization": f'Basic {credential}',
        "content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.request("POST", url=URL_TOKEN, data=data, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)
        token = data['access_token']
    else:
        token = None
    return (response.status_code, token)

def processa_consulta(token, cpf):

    headers = {
        "Authorization": f'Bearer {token}',
        "accept": "application/json",
    }

    url = URL_CONSULTA + cpf
    response = requests.request("GET", url=url, headers=headers)

    return response


def consulta_cpf(cpf):
    global token

    # first time, get token
    status = 200
    if not token:
        status, token = generate_bearer_token()
    if status != 200:
        return (500, None)

    response = processa_consulta(token, cpf)

    if response.status_code == 401:
        # token vencido, gera novo e reexecuta consulta
        print("token vencido")
        status, token = generate_bearer_token()
        if status != 200:
            return (500, None)
        response = processa_consulta(token, cpf)
    else:
        print("token reutilizado")
        
    if response.status_code == 200:
        data = json.loads(response.text)
    else:
        data = None
    return data

def verifica_nome_cpf(nome,cpf):

    #if DEBUG:
    #    return True    
    
    cpf = re.sub(r'\D', '', cpf)
    data = consulta_cpf(cpf)
    if not data:
        return False
    if data['situacao']['codigo'] != '0':
        print("situação", data['situacao']['codigo'])
        return False
    nome_cliente = nome.upper()
    nome_receita = data['nome'].upper()
    nome_cliente_limpo = nome_cliente.replace(' DE ', ' ')
    nome_cliente_limpo = nome_cliente_limpo.replace(' DA ', ' ')
    nome_cliente_limpo = nome_cliente_limpo.replace(' DO ', ' ')
    nome_cliente_limpo = unidecode.unidecode(nome_cliente_limpo)
    nome_receita_limpo = nome_receita.replace(' DE ', ' ')
    nome_receita_limpo = nome_receita_limpo.replace(' DA ', ' ')
    nome_receita_limpo = nome_receita_limpo.replace(' DO ', ' ')
    nome_receita_limpo = unidecode.unidecode(nome_receita_limpo)

    
    if nome_receita_limpo != nome_cliente_limpo:
        print("nome_cliente", nome_cliente)
        print("nome_receita", nome_receita)
        return False
    return True
