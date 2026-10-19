"""
services.py - Integração com a API ViaCEP.

Concentra toda a comunicação com o serviço externo num único lugar. As views
não sabem como a consulta é feita: só chamam consultar_cep() e tratam as
exceções. Se um dia o ViaCEP for trocado por outro provedor, só este arquivo muda.
"""
from django.http import HttpResponse
import re
import requests

URL_VIACEP = 'https://viacep.com.br/ws/{cep}/json/'

# Sem tempo limite, uma API lenta deixaria o nosso servidor travado esperando.
TIMEOUT_SEGUNDOS = 5


# Três exceções, porque são três falhas diferentes, com mensagens diferentes.
class CepInvalido(Exception):
    """O texto digitado não tem formato de CEP (8 números)."""


class CepNaoEncontrado(Exception):
    """Formato correto, mas o CEP não existe na base do ViaCEP."""


class ServicoCepIndisponivel(Exception):
    """Não houve resposta confiável do ViaCEP (rede, lentidão ou erro do servidor)."""


def limpar_cep(texto):
    """Mantém só os dígitos: '01001-000' vira '01001000'."""
    # [^0-9] aceita apenas 0-9 ASCII. Assim, o que vai para a URL
    # nunca contém barras, pontos ou outros caracteres que alterem o endereço
    # da requisição (proteção contra manipulação da URL).
    return re.sub(r'[^0-9]', '', texto or '')


def consultar_cep(cep_digitado):
    """
    Consulta o CEP no ViaCEP e devolve um dicionário com o endereço.
    Levanta CepInvalido, CepNaoEncontrado ou ServicoCepIndisponivel.
    """
    cep = limpar_cep(cep_digitado)

    # A própria documentação do ViaCEP recomenda validar o formato antes de
    # consultar. Isso também evita gastar uma chamada externa à toa.
    if len(cep) != 8:
        raise CepInvalido('O CEP deve ter 8 números.')

    try:
        resposta = requests.get(URL_VIACEP.format(cep=cep), timeout=TIMEOUT_SEGUNDOS)
    except requests.RequestException:
        # Cobre sem internet, DNS, tempo esgotado e outras falhas de conexão.
        raise ServicoCepIndisponivel('Não foi possível conectar ao serviço de CEP.')

    if resposta.status_code == 400:
        raise CepInvalido('Formato de CEP inválido.')
    if resposta.status_code != 200:
        # 429 (limite de uso), 5xx (erro do servidor) etc.
        raise ServicoCepIndisponivel('O serviço de CEP respondeu com erro.')

    try:
        dados = resposta.json()
    except ValueError:
        raise ServicoCepIndisponivel('Resposta inesperada do serviço de CEP.')

    if not isinstance(dados, dict):
        raise ServicoCepIndisponivel('Resposta inesperada do serviço de CEP.')

    # CEP inexistente: o ViaCEP responde 200, mas com {"erro": ...}. A
    # documentação mostra o valor como o texto "true"; aceitamos o booleano
    # também, caso o formato mude.
    if dados.get('erro') in (True, 'true'):
        raise CepNaoEncontrado('Este CEP não existe.')

    return {
        'cep': cep,
        'rua': dados.get('logradouro', ''),
        'complemento': dados.get('complemento', ''),
        'bairro': dados.get('bairro', ''),
        'cidade': dados.get('localidade', ''),
        'uf': dados.get('uf', ''),
    }