from decimal import Decimal
import pytest
import requests
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from AppStoreLink.models import FOTO_LADO_MAXIMO, FOTO_TAMANHO_MAXIMO, caminho_foto_usuario, validar_foto
from AppStoreLink.services import CepInvalido, CepNaoEncontrado, ServicoCepIndisponivel, consultar_cep, limpar_cep
from AppStoreLink.views import _validar_nome_preco
from tests.conftest import CORPO_VIACEP_SP, RespostaFalsa, gerar_imagem

# ----------------------------- limpar_cep ---------------------------------- #
@pytest.mark.parametrize("digitado, esperado", [
    ("01001-000", "01001000"),
    ("01.001-000", "01001000"),
    ("  01001000 ", "01001000"),
    ("abc", ""),
    (None, ""),
])
def test_limpar_cep_mantem_so_os_digitos(digitado, esperado):
    assert limpar_cep(digitado) == esperado

# ------------------------------- CT-010 ------------------------------------ #
def test_ct010_cep_valido_devolve_endereco_preenchido(viacep):
    """CT-010: CEP válido → o serviço devolve rua, bairro, cidade e UF vindos da API."""
    endereco = consultar_cep("01001-000")

    assert endereco == {
        "cep": "01001000",          # só dígitos
        "rua": "Praça da Sé",
        "complemento": "lado ímpar",
        "bairro": "Sé",
        "cidade": "São Paulo",
        "uf": "SP",
    }

def test_ct010_consulta_a_url_certa_do_viacep(monkeypatch):
    """CT-010: garante que a URL chamada é a do ViaCEP com o CEP só em dígitos."""
    import AppStoreLink.services as services
    chamadas = []

    def get_falso(url, timeout=None):
        chamadas.append((url, timeout))
        return RespostaFalsa(200, CORPO_VIACEP_SP)

    monkeypatch.setattr(services.requests, "get", get_falso)
    consultar_cep("01001-000")

    assert chamadas == [("https://viacep.com.br/ws/01001000/json/", services.TIMEOUT_SEGUNDOS)]

# ------------------------------- CT-011 ------------------------------------ #
@pytest.mark.parametrize("cep", ["123", "", "abcdefgh", "0100100000"])
def test_ct011_cep_com_formato_errado_e_barrado_sem_chamar_a_api(cep, monkeypatch):
    """CT-011: formato inválido (≠ 8 dígitos) → CepInvalido, e a API nem é consultada."""
    import AppStoreLink.services as services

    def nao_deveria_chamar(*a, **k):
        raise AssertionError("a API não deveria ser chamada para um CEP malformado")

    monkeypatch.setattr(services.requests, "get", nao_deveria_chamar)

    with pytest.raises(CepInvalido):
        consultar_cep(cep)


def test_ct011_cep_inexistente_levanta_cep_nao_encontrado(viacep):
    """CT-011: o ViaCEP responde 200 com {"erro": "true"} quando o CEP não existe."""
    viacep(RespostaFalsa(200, {"erro": "true"}))
    with pytest.raises(CepNaoEncontrado):
        consultar_cep("99999999")


def test_ct011_erro_booleano_tambem_e_tratado(viacep):
    viacep(RespostaFalsa(200, {"erro": True}))
    with pytest.raises(CepNaoEncontrado):
        consultar_cep("99999999")

def test_ct011_status_400_da_api_vira_cep_invalido(viacep):
    viacep(RespostaFalsa(400, {}))
    with pytest.raises(CepInvalido):
        consultar_cep("01001000")

@pytest.mark.parametrize("status", [429, 500, 503])
def test_ct011_erro_do_servidor_vira_servico_indisponivel(viacep, status):
    viacep(RespostaFalsa(status, {}))
    with pytest.raises(ServicoCepIndisponivel):
        consultar_cep("01001000")

@pytest.mark.parametrize("erro", [requests.ConnectionError(), requests.Timeout()])
def test_ct011_sem_internet_ou_timeout_vira_servico_indisponivel(viacep, erro):
    viacep(erro=erro)
    with pytest.raises(ServicoCepIndisponivel):
        consultar_cep("01001000")

@pytest.mark.parametrize("resposta", [
    RespostaFalsa(200, json_invalido=True),   # corpo que não é JSON
    RespostaFalsa(200, ["lista", "inesperada"]),  # JSON que não é um dicionário
])
def test_ct011_resposta_inesperada_vira_servico_indisponivel(viacep, resposta):
    viacep(resposta)
    with pytest.raises(ServicoCepIndisponivel):
        consultar_cep("01001000")

# --------------------------- validar_foto (CT-013 / CT-052) ----------------- #
@pytest.mark.parametrize("nome, formato", [
    ("foto.png", "PNG"), ("foto.jpg", "JPEG"), ("foto.jpeg", "JPEG"), ("foto.webp", "WEBP"),
    ("FOTO.PNG", "PNG"),  # extensão em maiúsculas também vale
])
def test_ct052_foto_valida_e_aceita(nome, formato):
    validar_foto(gerar_imagem(nome, formato))  # não pode levantar erro


def test_ct052_foto_acima_de_2mb_e_recusada():
    arquivo = SimpleUploadedFile("grande.png", b"x" * (FOTO_TAMANHO_MAXIMO + 1))
    with pytest.raises(ValidationError, match="2 MB"):
        validar_foto(arquivo)


@pytest.mark.parametrize("nome", ["documento.pdf", "foto.gif", "foto.bmp", "foto"])
def test_ct052_extensao_nao_permitida_e_recusada(nome):
    with pytest.raises(ValidationError, match="Formato não permitido"):
        validar_foto(SimpleUploadedFile(nome, b"qualquer coisa"))


def test_ct052_texto_renomeado_para_jpg_e_recusado():
    """O conteúdo é conferido de verdade: um .txt renomeado para .jpg não passa."""
    with pytest.raises(ValidationError, match="não é uma imagem válida"):
        validar_foto(SimpleUploadedFile("falsa.jpg", b"isto e so texto"))


def test_ct052_formato_real_diferente_da_extensao_e_recusado():
    """GIF verdadeiro com extensão .png: extensão ok, mas o formato real não é permitido."""
    with pytest.raises(ValidationError, match="Formato não permitido"):
        validar_foto(gerar_imagem("gif_disfarcado.png", "GIF"))


def test_ct052_imagem_com_lado_maior_que_4000px_e_recusada():
    with pytest.raises(ValidationError, match="grande demais"):
        validar_foto(gerar_imagem("larga.png", "PNG", (FOTO_LADO_MAXIMO + 1, 10)))


def test_ct052_ponteiro_do_arquivo_volta_ao_inicio_para_poder_salvar():
    arquivo = gerar_imagem()
    validar_foto(arquivo)
    assert arquivo.tell() == 0


def test_ct052_nome_do_arquivo_salvo_e_aleatorio_e_mantem_a_extensao():
    nome1 = caminho_foto_usuario(None, "Minha Foto.PNG")
    nome2 = caminho_foto_usuario(None, "Minha Foto.PNG")
    assert nome1.startswith("usuarios/") and nome1.endswith(".png")
    assert nome1 != nome2                       # nunca reaproveita o nome enviado
    assert "Minha" not in nome1

# ----------------- _validar_nome_preco (CT-019 a CT-024) -------------------- #
@pytest.mark.parametrize("preco_txt, esperado", [
    ("10", Decimal("10.00")),
    ("12.5", Decimal("12.50")),
    ("6.70", Decimal("6.70")),
    ("0.01", Decimal("0.01")),
    ("99999999.99", Decimal("99999999.99")),
])
def test_ct019_nome_e_preco_validos_nao_geram_erro(preco_txt, esperado):
    erros, preco = _validar_nome_preco("Produto X", preco_txt)
    assert erros == []
    assert preco == esperado


def test_ct019_preco_com_virgula_vem_ja_convertido_pela_view():
    """A view troca ',' por '.' antes de chamar a função (6,70 → 6.70)."""
    erros, preco = _validar_nome_preco("Produto X", "6,70".replace(",", "."))
    assert erros == [] and preco == Decimal("6.70")

def test_ct019_nome_vazio_gera_erro():
    erros, _ = _validar_nome_preco("", "10")
    assert erros == ["O nome do produto é obrigatório."]

def test_ct022_rotulo_serve_para_servico():
    erros, _ = _validar_nome_preco("", "10", rotulo="serviço")
    assert erros == ["O nome do serviço é obrigatório."]

def test_ct019_nome_com_mais_de_100_caracteres_gera_erro():
    erros, _ = _validar_nome_preco("a" * 101, "10")
    assert "O nome deve ter no máximo 100 caracteres." in erros

@pytest.mark.parametrize("preco_txt", ["0", "-5", "nan", "infinity", "-0.01"])
def test_ct019_preco_zero_negativo_ou_nao_finito_gera_erro(preco_txt):
    erros, _ = _validar_nome_preco("Produto X", preco_txt)
    assert "O preço deve ser um número maior que zero." in erros

@pytest.mark.parametrize("preco_txt", ["", "abc", "1,2,3", "R$ 10"])
def test_ct019_preco_que_nao_e_numero_gera_erro(preco_txt):
    erros, preco = _validar_nome_preco("Produto X", preco_txt)
    assert erros == ["Informe um preço válido (exemplo: 12,50)."]
    assert preco is None

def test_ct019_preco_acima_do_limite_do_banco_gera_erro():
    erros, _ = _validar_nome_preco("Produto X", "100000000")
    assert "O preço informado é alto demais." in erros

def test_ct019_acumula_todos_os_erros_de_uma_vez():
    erros, _ = _validar_nome_preco("", "abc")
    assert len(erros) == 2