"""
Fixtures (dados e ajudantes) compartilhadas por TODOS os testes.

Uma fixture é uma função marcada com @pytest.fixture. Quando um teste declara
um parâmetro com o mesmo nome dela, o pytest executa a fixture e entrega o
resultado ao teste. Assim cada teste começa com o cenário pronto
(usuário, loja, produto...) sem repetir código.
"""
import io
import os

import pytest

# O Playwright usa um "event loop" assíncrono; o ORM do Django reclama quando é
# chamado dentro dele. Como aqui só estamos testando, liberamos o aviso.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

CATEGORIAS = [
    "Alimentos", "Moda", "Esportes", "Construção", "Saúde",
    "Pets", "Ambiente", "Tecnologia", "Beleza", "Outros",
]
SENHA_VALIDA = "Senha123"


def mensagens(response):
    """Lista os textos das mensagens (messages.error/success) geradas na requisição."""
    from django.contrib.messages import get_messages
    return [str(m) for m in get_messages(response.wsgi_request)]


# --------------------------------------------------------------------------- #
# Configuração geral
# --------------------------------------------------------------------------- #
@pytest.fixture(autouse=True)
def _hash_de_senha_rapido(settings):
    """O hash padrão do Django é lento de propósito. Nos testes usamos um rápido."""
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture(autouse=True)
def _arquivos_enviados_em_pasta_temporaria(settings, tmp_path):
    """Fotos enviadas durante os testes não podem sujar a pasta media/ real."""
    settings.MEDIA_ROOT = tmp_path / "media"


# --------------------------------------------------------------------------- #
# Dados de banco
# --------------------------------------------------------------------------- #
@pytest.fixture
def categorias(db):
    """As 10 categorias. get_or_create evita duplicar o que a migração 0002 já criou."""
    from AppStoreLink.models import Categoria
    return {n: Categoria.objects.get_or_create(tipo_categoria=n)[0] for n in CATEGORIAS}


@pytest.fixture
def usuario(db):
    from django.contrib.auth.hashers import make_password
    from AppStoreLink.models import Usuario
    return Usuario.objects.create(
        nome="Maria", sobrenome="Silva", email="maria@gmail.com",
        senha=make_password(SENHA_VALIDA), cpf="12345678901", telefone="11999998888",
    )


@pytest.fixture
def outro_usuario(db):
    from django.contrib.auth.hashers import make_password
    from AppStoreLink.models import Usuario
    return Usuario.objects.create(
        nome="João", sobrenome="Souza", email="joao@gmail.com",
        senha=make_password(SENHA_VALIDA), cpf="10987654321",
    )


@pytest.fixture
def client_logado(client, usuario):
    """Client do Django já 'logado'. O projeto usa login manual: guarda usuario_id na sessão."""
    sessao = client.session
    sessao["usuario_id"] = usuario.pk  # .pk serve qualquer que seja o nome da chave primária de Usuario
    sessao.save()
    return client


@pytest.fixture
def loja(db, categorias, usuario):
    from AppStoreLink.models import Endereco, Loja
    endereco = Endereco.objects.create(rua="Rua das Flores", numero_estabelecimento="100", cep="01001000")
    return Loja.objects.create(
        nome_loja="Padaria Central", email_loja="padaria@gmail.com", telefone_loja="11911112222",
        cnpj="12345678000199", link="https://padaria.example.com",
        id_endereco=endereco, id_categoria=categorias["Alimentos"], id_dono=usuario,
    )


@pytest.fixture
def produto(loja, categorias):
    from decimal import Decimal
    from AppStoreLink.models import Produto
    return Produto.objects.create(
        nome_produto="Pão Francês", preco=Decimal("1.50"), descricao="Pão quentinho",
        id_loja=loja, id_categoria=categorias["Alimentos"],
    )


@pytest.fixture
def servico(loja):
    from decimal import Decimal
    from AppStoreLink.models import Servico
    return Servico.objects.create(
        nome_servico="Entrega Express", preco=Decimal("9.90"), descricao="Entrega em 30 min", id_loja=loja,
    )


# --------------------------------------------------------------------------- #
# ViaCEP falso (nunca chamamos a internet de verdade nos testes)
# --------------------------------------------------------------------------- #
class RespostaFalsa:
    """Imita o objeto que requests.get() devolve."""

    def __init__(self, status_code=200, corpo=None, json_invalido=False):
        self.status_code = status_code
        self._corpo = corpo
        self._json_invalido = json_invalido

    def json(self):
        if self._json_invalido:
            raise ValueError("não é JSON")
        return self._corpo


CORPO_VIACEP_SP = {
    "cep": "01001-000", "logradouro": "Praça da Sé", "complemento": "lado ímpar",
    "bairro": "Sé", "localidade": "São Paulo", "uf": "SP",
}


@pytest.fixture
def viacep(monkeypatch):
    """
    Devolve uma função para escolher o que o 'ViaCEP falso' responde.
    Uso:  viacep(RespostaFalsa(200, CORPO_VIACEP_SP))   ou   viacep(erro=requests.ConnectionError())
    Por padrão responde com sucesso (Praça da Sé).
    """
    import AppStoreLink.services as services

    def configurar(resposta=None, erro=None):
        def get_falso(url, timeout=None):
            if erro is not None:
                raise erro
            return resposta
        monkeypatch.setattr(services.requests, "get", get_falso)

    configurar(RespostaFalsa(200, CORPO_VIACEP_SP))
    return configurar


# --------------------------------------------------------------------------- #
# Imagens de teste
# --------------------------------------------------------------------------- #
def gerar_imagem(nome="foto.png", formato="PNG", tamanho=(20, 20)):
    """Cria uma imagem de verdade, em memória, pronta para 'enviar' num formulário."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image
    buffer = io.BytesIO()
    Image.new("RGB", tamanho, "red").save(buffer, format=formato)
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type=f"image/{formato.lower()}")


@pytest.fixture
def imagem():
    return gerar_imagem


# --------------------------------------------------------------------------- #
# Marcadores automáticos por pasta (permite rodar: pytest -m unit)
# --------------------------------------------------------------------------- #
def pytest_collection_modifyitems(items):
    for item in items:
        caminho = str(item.fspath)
        if f"{os.sep}unit{os.sep}" in caminho:
            item.add_marker(pytest.mark.unit)
        elif f"{os.sep}integration{os.sep}" in caminho:
            item.add_marker(pytest.mark.integration)
        elif f"{os.sep}e2e{os.sep}" in caminho:
            item.add_marker(pytest.mark.e2e)