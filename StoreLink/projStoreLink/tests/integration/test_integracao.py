import re
from decimal import Decimal
from urllib.parse import urlparse
import pytest
import requests
from playwright.sync_api import expect
from django.contrib.auth.hashers import check_password
from django.contrib.staticfiles import finders
from django.test import Client
from django.urls import NoReverseMatch, resolve, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from AppStoreLink.models import Avaliacao, Endereco, Loja, LojaFavoritas, Produto, Servico, Usuario
from tests.conftest import CATEGORIAS, RespostaFalsa, SENHA_VALIDA, mensagens

# CT-005 (bloco "Cadastro de usuário")
DADOS_CADASTRO = {
    "nome": "Ana", "sobrenome": "Lima", "email": "ana@gmail.com",
    "cpf": "98765432100", "telefone": "11988887777", "senha": SENHA_VALIDA,
}


@pytest.mark.django_db
def test_ct005_cadastro_valido_cria_usuario_e_redireciona_para_login(client):
    resposta = client.post(reverse("cadastro"), DADOS_CADASTRO)

    assert resposta.status_code == 302
    assert resposta.url == reverse("login")
    usuario = Usuario.objects.get(email="ana@gmail.com")
    assert usuario.nome == "Ana"
    assert usuario.senha != SENHA_VALIDA                 # nunca guarda a senha em texto puro
    assert check_password(SENHA_VALIDA, usuario.senha)
    assert any("Cadastro realizado" in m for m in mensagens(resposta))


@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor, trecho_da_mensagem", [
    ("email", "ana@exemplo.com", "serviço de email"),     # domínio fora da lista aceita
    ("email", "", "serviço de email"),
    ("senha", "curta1A", "mínimo 8 caracteres"),
    ("senha", "semnumeroAAA", "mínimo 8 caracteres"),
    ("senha", "SEMMINUSCULA1", "mínimo 8 caracteres"),
    ("senha", "semmaiuscula1", "mínimo 8 caracteres"),
    ("cpf", "123", "11 números"),
])
def test_ct005_cadastro_com_dados_invalidos_nao_cria_usuario(client, campo, valor, trecho_da_mensagem):
    dados = {**DADOS_CADASTRO, campo: valor}
    resposta = client.post(reverse("cadastro"), dados)

    assert resposta.status_code == 200                   # volta para o formulário (não redireciona)
    assert Usuario.objects.count() == 0
    assert any(trecho_da_mensagem in m for m in mensagens(resposta))

@pytest.mark.django_db
@pytest.mark.parametrize("dominio", ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "ymail.com"])
def test_ct005_cadastro_aceita_os_provedores_de_email_permitidos(client, dominio):
    resposta = client.post(reverse("cadastro"), {**DADOS_CADASTRO, "email": f"ana@{dominio}"})

    assert resposta.status_code == 302 and resposta.url == reverse("login")
    assert Usuario.objects.filter(email=f"ana@{dominio}").exists()


@pytest.mark.django_db
def test_ct005_email_ou_cpf_ja_cadastrados_sao_recusados(client, usuario):
    r1 = client.post(reverse("cadastro"), {**DADOS_CADASTRO, "email": usuario.email})
    r2 = client.post(reverse("cadastro"), {**DADOS_CADASTRO, "cpf": usuario.cpf})

    assert any("e-mail já está cadastrado" in m for m in mensagens(r1))
    assert any("CPF já está cadastrado" in m for m in mensagens(r2))
    assert Usuario.objects.count() == 1


@pytest.mark.django_db
def test_ct005_tela_de_cadastro_abre_com_o_formulario(client):
    resposta = client.get(reverse("cadastro"))
    assert resposta.status_code == 200
    for campo in ("nome", "sobrenome", "email", "cpf", "telefone", "senha"):
        assert f'name="{campo}"' in resposta.content.decode()



# CT-053 a CT-057 (bloco "Login")
@pytest.mark.django_db
def test_ct053_login_credenciais_validas_autentica_e_vai_para_o_perfil(client, usuario):
    resposta = client.post(reverse("login"), {"email": usuario.email, "senha": SENHA_VALIDA})

    assert resposta.status_code == 302
    assert resposta.url == reverse("perfil-consumidor")
    assert client.session["usuario_id"] == usuario.pk


@pytest.mark.django_db
def test_ct054_login_senha_incorreta_nao_autentica(client, usuario):
    resposta = client.post(reverse("login"), {"email": usuario.email, "senha": "SenhaErrada1"})

    assert resposta.status_code == 200
    assert "usuario_id" not in client.session
    assert any("inválidos" in m for m in mensagens(resposta))


@pytest.mark.django_db
def test_ct055_login_email_nao_cadastrado_nao_autentica(client):
    resposta = client.post(reverse("login"), {"email": "fantasma@gmail.com", "senha": "Qualquer1"})

    assert resposta.status_code == 200
    assert "usuario_id" not in client.session
    assert any("inválidos" in m for m in mensagens(resposta))


@pytest.mark.django_db
def test_ct056_login_sem_email_nao_autentica(client, usuario):
    """No navegador o atributo `required` já barra; aqui provamos que o SERVIDOR também barra."""
    resposta = client.post(reverse("login"), {"email": "", "senha": SENHA_VALIDA})

    assert resposta.status_code == 200
    assert "usuario_id" not in client.session
    assert mensagens(resposta)  # existe mensagem de erro


@pytest.mark.django_db
def test_ct057_login_sem_senha_nao_autentica(client, usuario):
    resposta = client.post(reverse("login"), {"email": usuario.email, "senha": ""})

    assert resposta.status_code == 200
    assert "usuario_id" not in client.session


@pytest.mark.django_db
def test_ct053_formulario_de_login_exige_email_e_senha_no_html(client):
    html = client.get(reverse("login")).content.decode()
    assert 'name="email"' in html and 'name="senha"' in html
    assert html.count("required") >= 2



# CT-017 (logout no perfil da loja) e CT-052 (logout no perfil do consumidor)
@pytest.mark.django_db
@pytest.mark.parametrize("pagina", ["perfil-loja", "perfil-consumidor"])
def test_ct017_ct052_pagina_logada_mostra_botao_de_logout(client_logado, pagina):
    html = client_logado.get(reverse(pagina)).content.decode()
    assert f'action="{reverse("logout")}"' in html
    assert "Fazer Logout" in html


@pytest.mark.django_db
def test_ct017_ct052_logout_encerra_a_sessao_e_bloqueia_area_restrita(client_logado):
    resposta = client_logado.post(reverse("logout"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("index")
    assert "usuario_id" not in client_logado.session

    # Área restrita sem nova autenticação → manda para o login
    restrita = client_logado.get(reverse("perfil-consumidor"))
    assert restrita.status_code == 302
    assert restrita.url == reverse("login")


@pytest.mark.django_db
def test_ct052_logout_so_aceita_post(client_logado):
    assert client_logado.get(reverse("logout")).status_code == 405
    assert client_logado.session["usuario_id"]  # continua logado



# CT-025 a CT-030 (Recuperar senha: e-mail -> link enviado por e-mail -> nova senha)
URL = "recuperar-senha"
NOVA_SENHA = "NovaSenha456"

def trecho_do_campo(html, campo):
    """Devolve o pedaço do HTML em volta de name="campo" (onde fica o atributo required)."""
    pos = html.index(f'name="{campo}"')
    return html[pos - 80: pos + 80]

@pytest.fixture
def link_de_redefinicao(client, usuario, mailoutbox):
    """Passo 1 feito: pede o link e devolve o caminho (/redefinir-senha/...) lido do e-mail enviado."""
    client.post(reverse(URL), {"email": usuario.email})
    link = re.search(r"https?://\S+", mailoutbox[-1].body).group(0)
    return urlparse(link).path


# ------------------------------- CT-025 ------------------------------------ #
@pytest.mark.django_db
def test_ct025_pedir_o_link_envia_um_email_ao_usuario_cadastrado(client, usuario, mailoutbox):
    resposta = client.post(reverse(URL), {"email": usuario.email})

    assert resposta.status_code == 302 and resposta.url == reverse("login")
    assert any("enviamos um link" in m for m in mensagens(resposta))
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [usuario.email]
    assert "Redefinição de senha" in mailoutbox[0].subject
    link = re.search(r"https?://\S+", mailoutbox[0].body).group(0)
    assert resolve(urlparse(link).path).url_name == "redefinir-senha"   # o link aponta para a tela de nova senha

@pytest.mark.django_db
def test_ct025_link_do_email_abre_a_tela_de_nova_senha(client, link_de_redefinicao):
    resposta = client.get(link_de_redefinicao)

    html = resposta.content.decode()
    assert resposta.status_code == 200
    assert 'name="nova_senha"' in html and 'name="confirmar_senha"' in html

@pytest.mark.django_db
def test_ct025_redefinir_senha_com_dados_validos_troca_a_senha(client, usuario, link_de_redefinicao):
    resposta = client.post(link_de_redefinicao, {"nova_senha": NOVA_SENHA, "confirmar_senha": NOVA_SENHA})

    assert resposta.status_code == 302 and resposta.url == reverse("login")
    assert any("Senha alterada com sucesso" in m for m in mensagens(resposta))
    usuario.refresh_from_db()
    assert check_password(NOVA_SENHA, usuario.senha)
    assert not check_password(SENHA_VALIDA, usuario.senha)

    # "A nova senha deve permitir o acesso à conta"
    login = client.post(reverse("login"), {"email": usuario.email, "senha": NOVA_SENHA})
    assert login.status_code == 302 and client.session["usuario_id"] == usuario.pk

@pytest.mark.django_db
def test_ct025_o_link_so_vale_uma_vez(client, usuario, link_de_redefinicao):
    client.post(link_de_redefinicao, {"nova_senha": NOVA_SENHA, "confirmar_senha": NOVA_SENHA})
    senha_depois = Usuario.objects.get(pk=usuario.pk).senha

    # a senha mudou, então o token do mesmo link deixa de valer
    segunda = client.post(link_de_redefinicao, {"nova_senha": "OutraSenha789", "confirmar_senha": "OutraSenha789"})

    assert segunda.status_code == 302 and segunda.url == reverse(URL)
    assert any("inválido ou expirou" in m for m in mensagens(segunda))
    assert Usuario.objects.get(pk=usuario.pk).senha == senha_depois

@pytest.mark.django_db
@pytest.mark.parametrize("uid, token", [
    ("uid-que-nao-e-base64-@@", "abc-123"),                        # uid adulterado
    (urlsafe_base64_encode(force_bytes(999999)), "abc-123"),       # usuário que não existe
])
def test_ct025_link_adulterado_ou_de_usuario_inexistente_e_recusado(client, usuario, uid, token):
    senha_antes = usuario.senha
    link = reverse("redefinir-senha", kwargs={"uidb64": uid, "token": token})

    resposta = client.post(link, {"nova_senha": NOVA_SENHA, "confirmar_senha": NOVA_SENHA})

    assert resposta.status_code == 302 and resposta.url == reverse(URL)
    assert any("inválido ou expirou" in m for m in mensagens(resposta))
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes

@pytest.mark.django_db
def test_ct025_token_errado_para_usuario_existente_e_recusado(client, usuario):
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    link = reverse("redefinir-senha", kwargs={"uidb64": uid, "token": "abc-123"})

    resposta = client.get(link)

    assert resposta.status_code == 302 and resposta.url == reverse(URL)


# ------------------------------- CT-026 ------------------------------------ #
@pytest.mark.django_db
def test_ct026_email_nao_cadastrado_nao_envia_link_nem_altera_nada(client, usuario, mailoutbox):
    senha_antes = usuario.senha

    resposta = client.post(reverse(URL), {"email": "naoexiste@gmail.com"})

    assert resposta.status_code == 302 and resposta.url == reverse("login")
    assert mailoutbox == []                       # nenhum e-mail com link foi enviado
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes

@pytest.mark.django_db
def test_ct026_resposta_e_igual_para_email_cadastrado_e_nao_cadastrado(usuario):
    """A view responde igual nos dois casos de propósito: não revela quem tem conta no site."""
    existente = Client().post(reverse(URL), {"email": usuario.email})          # um navegador para cada pedido,
    inexistente = Client().post(reverse(URL), {"email": "naoexiste@gmail.com"})  # senão as mensagens se acumulam

    assert (existente.status_code, existente.url) == (inexistente.status_code, inexistente.url)
    assert mensagens(existente) == mensagens(inexistente)


# ------------------------------- CT-027 ------------------------------------ #
@pytest.mark.django_db
def test_ct027_senhas_diferentes_nao_alteram_a_senha(client, usuario, link_de_redefinicao):
    senha_antes = usuario.senha

    resposta = client.post(link_de_redefinicao, {"nova_senha": NOVA_SENHA, "confirmar_senha": "OutraSenha789"})

    assert resposta.status_code == 200
    assert any("não estão iguais" in m for m in mensagens(resposta))
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes
    assert client.get(link_de_redefinicao).status_code == 200       # o link continua valendo para tentar de novo


# ------------------------------- CT-028 ------------------------------------ #
@pytest.mark.django_db
def test_ct028_sem_email_nao_envia_link(client, usuario, mailoutbox):
    senha_antes = usuario.senha

    resposta = client.post(reverse(URL), {"email": ""})

    assert resposta.status_code == 302
    assert mailoutbox == []
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes

@pytest.mark.django_db
def test_ct028_html_marca_o_email_como_obrigatorio(client):
    html = client.get(reverse(URL)).content.decode()

    assert "required" in trecho_do_campo(html, "email")      # é o navegador que pede o preenchimento


# ------------------------------- CT-029 ------------------------------------ #
@pytest.mark.django_db
def test_ct029_sem_nova_senha_nao_altera_a_senha(client, usuario, link_de_redefinicao):
    senha_antes = usuario.senha

    resposta = client.post(link_de_redefinicao, {"nova_senha": "", "confirmar_senha": NOVA_SENHA})

    assert resposta.status_code == 200
    assert mensagens(resposta)
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes

@pytest.mark.django_db
def test_ct029_ct030_html_marca_os_dois_campos_de_senha_como_obrigatorios(client, link_de_redefinicao):
    html = client.get(link_de_redefinicao).content.decode()

    for campo in ("nova_senha", "confirmar_senha"):
        assert "required" in trecho_do_campo(html, campo)

@pytest.mark.django_db
def test_extra_redefinir_senha_nao_aceita_senha_vazia(client, usuario, link_de_redefinicao):
    senha_antes = usuario.senha

    resposta = client.post(link_de_redefinicao, {"nova_senha": "", "confirmar_senha": ""})

    assert resposta.status_code == 200
    assert any("A senha precisa conter" in m for m in mensagens(resposta))
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes

@pytest.mark.django_db
@pytest.mark.parametrize("senha", ["Abc123", "senha1234", "SENHA1234", "SenhaForte"])   # curta, sem maiúscula, sem minúscula, sem número
def test_extra_nova_senha_fora_da_regra_do_cadastro_e_recusada(client, usuario, link_de_redefinicao, senha):
    senha_antes = usuario.senha

    resposta = client.post(link_de_redefinicao, {"nova_senha": senha, "confirmar_senha": senha})

    assert resposta.status_code == 200
    assert any("A senha precisa conter" in m for m in mensagens(resposta))
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes


# ------------------------------- CT-030 ------------------------------------ #
@pytest.mark.django_db
def test_ct030_sem_confirmar_a_nova_senha_nao_altera_a_senha(client, usuario, link_de_redefinicao):
    senha_antes = usuario.senha

    resposta = client.post(link_de_redefinicao, {"nova_senha": NOVA_SENHA, "confirmar_senha": ""})

    assert resposta.status_code == 200
    assert mensagens(resposta)
    usuario.refresh_from_db()
    assert usuario.senha == senha_antes

@pytest.fixture
def pagina_da_loja(loja):
    return f"http://testserver{reverse('InformacoesLoja', args=[loja.id_loja])}"

def avaliar_loja(client, loja, nota, comentario, referer=None):
    extra = {"HTTP_REFERER": referer} if referer else {}
    dados = {"comentario": comentario}
    if nota is not None:
        dados["nota"] = nota
    return client.post(reverse("avaliar-loja", args=[loja.id_loja]), dados, **extra)

# ------------------------------- CT-038 ------------------------------------ #
@pytest.mark.django_db
def test_ct038_publicar_comentario_com_nota_valida(client_logado, usuario, loja, pagina_da_loja):
    resposta = avaliar_loja(client_logado, loja, 5, "Ótimo atendimento e produtos de qualidade.", pagina_da_loja)

    assert resposta.status_code == 302 and resposta.url == pagina_da_loja
    assert any("Avaliação salva" in m for m in mensagens(resposta))
    av = Avaliacao.objects.get()
    assert (av.nota, av.comentario) == (5, "Ótimo atendimento e produtos de qualidade.")
    assert av.id_usuario == usuario and av.id_loja == loja
    assert av.id_produto is None and av.id_servico is None

@pytest.mark.django_db
@pytest.mark.parametrize("nota", [1, 2, 3, 4, 5])
def test_ct038_aceita_todas_as_notas_de_1_a_5(client_logado, loja, nota):
    avaliar_loja(client_logado, loja, nota, "ok")
    assert Avaliacao.objects.get().nota == nota

@pytest.mark.django_db
def test_ct038_comentario_exige_login(client, loja):
    resposta = avaliar_loja(client, loja, 5, "ok")
    assert resposta.url == reverse("login")
    assert not Avaliacao.objects.exists()

@pytest.mark.django_db
def test_ct038_comentario_acima_de_1000_caracteres_e_recusado(client_logado, loja):
    resposta = avaliar_loja(client_logado, loja, 5, "a" * 1001)
    assert not Avaliacao.objects.exists()
    assert any("no máximo 1000" in m for m in mensagens(resposta))


# ------------------------------- CT-039 ------------------------------------ #
@pytest.mark.django_db
@pytest.mark.parametrize("nota", [None, "", "0", "6", "-1", "abc"])
def test_ct039_sem_nota_valida_o_comentario_nao_e_enviado(client_logado, loja, nota):
    resposta = avaliar_loja(client_logado, loja, nota, "Comentário sem estrelas")

    assert not Avaliacao.objects.exists()
    assert any("nota deve ser um número de 1 a 5" in m for m in mensagens(resposta))

# ------------------------------- CT-040 ------------------------------------ #
@pytest.mark.django_db
def test_ct040_comentario_aparece_na_tela_da_loja_e_continua_apos_atualizar(client_logado, loja, pagina_da_loja):
    avaliar_loja(client_logado, loja, 4, "Boa experiência de compra.", pagina_da_loja)
    url = reverse("InformacoesLoja", args=[loja.id_loja])

    primeira = client_logado.get(url)
    atualizada = client_logado.get(url)        # "atualizar a página" = nova requisição

    for pagina in (primeira, atualizada):
        assert "Boa experiência de compra." in pagina.content.decode()
        assert [(a.nota, a.comentario) for a in pagina.context["avaliacoes"]] == [(4, "Boa experiência de compra.")]

# ------------------------------- CT-041 ------------------------------------ #
@pytest.mark.django_db
def test_ct041_mesmo_usuario_nao_consegue_ter_dois_comentarios_na_mesma_loja(client_logado, usuario, loja):
    avaliar_loja(client_logado, loja, 5, "Primeiro comentário")
    avaliar_loja(client_logado, loja, 3, "Segundo comentário, diferente")

    assert Avaliacao.objects.filter(id_usuario=usuario, id_loja=loja).count() == 1

@pytest.mark.django_db
def test_ct041_observacao_segundo_envio_substitui_o_texto_do_primeiro(client_logado, loja):
    """
    ATENÇÃO (comportamento real do sistema): em vez de BLOQUEAR o 2º envio, a view o trata como
    edição (update_or_create). O limite de 1 por usuário é garantido, mas o comentário antigo
    é sobrescrito e não "preservado" como o CT-041 descreve. Se o TCC exigir preservar o antigo,
    é preciso mudar a view; se aceitar "só existe 1", ajuste o texto do CT-041.
    """
    avaliar_loja(client_logado, loja, 5, "Primeiro comentário")
    avaliar_loja(client_logado, loja, 3, "Segundo comentário, diferente")

    av = Avaliacao.objects.get()
    assert (av.nota, av.comentario) == (3, "Segundo comentário, diferente")

# ------------------------------- CT-042 ------------------------------------ #
@pytest.mark.django_db
def test_ct042_editar_comentario_atualiza_o_existente_sem_criar_outro(client_logado, loja):
    avaliar_loja(client_logado, loja, 3, "Atendimento razoável")
    original = Avaliacao.objects.get()

    avaliar_loja(client_logado, loja, 5, "Minha experiência foi excelente.")

    assert Avaliacao.objects.count() == 1
    editado = Avaliacao.objects.get()
    assert editado.pk == original.pk                         # mesmo registro
    assert (editado.nota, editado.comentario) == (5, "Minha experiência foi excelente.")

@pytest.mark.django_db
def test_ct042_tela_mostra_botao_de_editar_so_para_o_dono_do_comentario(client_logado, outro_usuario, loja, usuario):
    Avaliacao.objects.create(nota=4, comentario="meu", id_usuario=usuario, id_loja=loja)
    Avaliacao.objects.create(nota=2, comentario="do outro", id_usuario=outro_usuario, id_loja=loja)

    html = client_logado.get(reverse("InformacoesLoja", args=[loja.id_loja])).content.decode()
    assert html.count('class="info-comentario-editar"') == 1

# ------------------------------- CT-043 ------------------------------------ #
@pytest.mark.django_db
def test_ct043_visitante_ve_comentarios_e_notas_de_outros_usuarios_na_loja(client, usuario, outro_usuario, loja):
    Avaliacao.objects.create(nota=5, comentario="Adorei!", id_usuario=usuario, id_loja=loja)
    Avaliacao.objects.create(nota=2, comentario="Demorou muito.", id_usuario=outro_usuario, id_loja=loja)

    resposta = client.get(reverse("InformacoesLoja", args=[loja.id_loja]))   # sem login
    html = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Adorei!" in html and "Demorou muito." in html
    assert "Maria" in html and "João" in html
    assert sorted(a.nota for a in resposta.context["avaliacoes"]) == [2, 5]

@pytest.mark.django_db
def test_ct043_loja_sem_comentarios_mostra_aviso(client, loja):
    assert "Nenhum comentário cadastrado" in client.get(reverse("InformacoesLoja", args=[loja.id_loja])).content.decode()

@pytest.mark.django_db
def test_ct043_nota_sem_texto_aparece_com_o_texto_padrao(client_logado, loja):
    avaliar_loja(client_logado, loja, 5, "")

    avaliacoes = client_logado.get(reverse("InformacoesLoja", args=[loja.id_loja])).context["avaliacoes"]
    assert [(a.nota, a.comentario) for a in avaliacoes] == [(5, "(Sem comentário)")]

@pytest.mark.django_db
@pytest.mark.xfail(strict=True, reason=(
    "FUNCIONALIDADE NÃO IMPLEMENTADA: as views InformacoesProduto e InformacoesServico não enviam "
    "as avaliações para o template, então os comentários de produtos/serviços não são exibidos."
))
def test_ct043_comentarios_de_produto_aparecem_na_tela_do_produto(client, usuario, produto):
    Avaliacao.objects.create(nota=5, comentario="Muito bom mesmo", id_usuario=usuario, id_produto=produto)
    html = client.get(reverse("InformacoesProduto", args=[produto.id_loja_id])).content.decode()
    assert "Muito bom mesmo" in html

# ------------------------------- CT-044 ------------------------------------ #
@pytest.mark.django_db
@pytest.mark.parametrize("rota, fixture_alvo, campo", [
    ("avaliar-loja", "loja", "id_loja"),
    ("avaliar-produto", "produto", "id_produto"),
    ("avaliar-servico", "servico", "id_servico"),
])
def test_ct044_um_unico_comentario_por_usuario_em_cada_item(request, client_logado, usuario, rota, fixture_alvo, campo):
    alvo = request.getfixturevalue(fixture_alvo)
    url = reverse(rota, args=[alvo.pk])

    client_logado.post(url, {"nota": 5, "comentario": "primeiro"})
    client_logado.post(url, {"nota": 1, "comentario": "segundo"})

    assert Avaliacao.objects.filter(id_usuario=usuario, **{campo: alvo}).count() == 1

@pytest.mark.django_db
def test_ct044_usuarios_diferentes_podem_comentar_o_mesmo_item(client, usuario, outro_usuario, loja):
    for u in (usuario, outro_usuario):
        sessao = client.session
        sessao["usuario_id"] = u.pk
        sessao.save()
        avaliar_loja(client, loja, 5, f"comentário de {u.nome}")
    assert Avaliacao.objects.filter(id_loja=loja).count() == 2

def buscar(client, termo):
    return client.get(reverse("buscar"), {"q": termo})

# ------------------------------- CT-031 ------------------------------------ #
@pytest.mark.django_db
def test_ct031_pesquisar_loja_pelo_nome(client, loja):
    resposta = buscar(client, "Padaria Central")

    assert resposta.status_code == 200
    assert "AppStoreLink/buscar.html" in [t.name for t in resposta.templates]
    assert list(resposta.context["lojas"]) == [loja]
    assert "Padaria Central" in resposta.content.decode()

@pytest.mark.django_db
def test_ct031_pesquisa_ignora_maiusculas_e_aceita_parte_do_nome(client, loja):
    assert list(buscar(client, "padaria").context["lojas"]) == [loja]   # "padaria" ≠ "Padaria Central" em maiúsculas/tamanh

@pytest.mark.django_db
def test_ct031_formulario_da_tela_inicial_envia_para_buscar(client):
    html = client.get(reverse("index")).content.decode()
    assert f'action="{reverse("buscar")}"' in html and 'method="GET"' in html and 'name="q"' in html

# ------------------------------- CT-032 ------------------------------------ #
@pytest.mark.django_db
def test_ct032_pesquisar_produto(client, produto):
    resposta = buscar(client, "Pão Francês")

    assert list(resposta.context["produtos"]) == [produto]
    assert "Pão Francês" in resposta.content.decode()

# ------------------------------- CT-033 ------------------------------------ #
@pytest.mark.django_db
def test_ct033_pesquisar_servico(client, servico):
    resposta = buscar(client, "Entrega Express")

    assert list(resposta.context["servicos"]) == [servico]
    assert "Entrega Express" in resposta.content.decode()

# ------------------------------- CT-034 ------------------------------------ #
@pytest.mark.django_db
def test_ct034_termo_sem_correspondencia_mostra_nenhum_resultado(client, loja, produto, servico):
    resposta = buscar(client, "zzzxxyyqq")

    assert resposta.status_code == 200
    assert resposta.context["total_resultados"] == 0
    assert not resposta.context["lojas"] and not resposta.context["produtos"] and not resposta.context["servicos"]
    html = resposta.content.decode()
    assert "Nenhum resultado encontrado" in html
    assert "Padaria Central" not in html and "Pão Francês" not in html

@pytest.mark.django_db
@pytest.mark.parametrize("termo", ["", "   "])
def test_ct034_pesquisa_vazia_nao_lista_nada(client, loja, termo):
    assert buscar(client, termo).context["total_resultados"] == 0

@pytest.mark.django_db
def test_ct034_nao_traz_registros_que_nao_correspondem(client, loja, produto, servico):
    resposta = buscar(client, "Pão")
    assert [p.nome_produto for p in resposta.context["produtos"]] == ["Pão Francês"]
    assert not resposta.context["servicos"]

# ------------------------- CT-035 / CT-036 / CT-037 ------------------------- #
@pytest.mark.django_db
def test_ct035_resultado_de_loja_aponta_para_a_tela_da_loja(client, loja):
    html = buscar(client, "Padaria").content.decode()
    alvo = reverse("InformacoesLoja", args=[loja.id_loja])
    assert f'data-url="{alvo}"' in html
    assert client.get(alvo).status_code == 200
    assert "Padaria Central" in client.get(alvo).content.decode()

@pytest.mark.django_db
def test_ct036_resultado_de_produto_aponta_para_a_tela_de_produtos_da_loja(client, produto):
    html = buscar(client, "Pão Francês").content.decode()
    alvo = reverse("InformacoesProduto", args=[produto.id_loja_id])
    assert f'data-url="{alvo}"' in html
    pagina = client.get(alvo)
    assert pagina.status_code == 200 and "Pão Francês" in pagina.content.decode()

@pytest.mark.django_db
def test_ct037_resultado_de_servico_aponta_para_a_tela_de_servicos_da_loja(client, servico):
    html = buscar(client, "Entrega Express").content.decode()
    alvo = reverse("InformacoesServico", args=[servico.id_loja_id])
    assert f'data-url="{alvo}"' in html
    pagina = client.get(alvo)
    assert pagina.status_code == 200 and "Entrega Express" in pagina.content.decode()

# ------------------------------- CT-009 ------------------------------------ #
@pytest.mark.django_db
def test_ct009_salvar_nome_e_sobrenome(client_logado, usuario):
    resposta = client_logado.post(reverse("editar-consumidor"), {"nome": "Mariana", "sobrenome": "Oliveira"})

    assert resposta.status_code == 302 and resposta.url == reverse("perfil-consumidor")
    assert any("atualizado com sucesso" in m for m in mensagens(resposta))
    usuario.refresh_from_db()
    assert (usuario.nome, usuario.sobrenome) == ("Mariana", "Oliveira")

    html = client_logado.get(reverse("perfil-consumidor")).content.decode()
    assert 'value="Mariana"' in html and 'value="Oliveira"' in html

@pytest.mark.django_db
def test_ct009_sobrenome_e_opcional(client_logado, usuario):
    client_logado.post(reverse("editar-consumidor"), {"nome": "Mariana", "sobrenome": "  "})
    usuario.refresh_from_db()
    assert usuario.nome == "Mariana" and usuario.sobrenome is None

@pytest.mark.django_db
def test_ct009_nome_vazio_nao_e_salvo(client_logado, usuario):
    resposta = client_logado.post(reverse("editar-consumidor"), {"nome": "   ", "sobrenome": "X"})

    assert any("precisa ter um nome" in m for m in mensagens(resposta))
    usuario.refresh_from_db()
    assert usuario.nome == "Maria"

@pytest.mark.django_db
def test_ct009_sem_login_nao_altera_ninguem(client, usuario):
    resposta = client.post(reverse("editar-consumidor"), {"nome": "Hacker", "sobrenome": "X"})
    assert resposta.status_code == 404
    usuario.refresh_from_db()
    assert usuario.nome == "Maria"

# ------------------------------- CT-047 ------------------------------------ #
@pytest.mark.django_db
def test_ct047_perfil_mostra_as_informacoes_do_usuario_autenticado(client_logado, usuario, outro_usuario):
    resposta = client_logado.get(reverse("perfil-consumidor"))
    html = resposta.content.decode()

    assert resposta.status_code == 200
    assert resposta.context["chave_perf_consm"] == usuario
    assert 'value="Maria"' in html and 'value="Silva"' in html
    assert "João" not in html                      # não vaza dados de outro usuário

@pytest.mark.django_db
def test_ct047_perfil_sem_login_redireciona_para_o_login(client):
    resposta = client.get(reverse("perfil-consumidor"))
    assert resposta.status_code == 302 and resposta.url == reverse("login")
    assert any("precisa fazer login" in m for m in mensagens(resposta))

# ------------------------------- CT-048 ------------------------------------ #
@pytest.mark.django_db
def test_ct048_favoritar_loja_registra_e_mostra_no_perfil(client_logado, usuario, loja):
    resposta = client_logado.post(reverse("favoritar-loja", args=[loja.id_loja]))

    assert resposta.status_code == 302 and resposta.url == reverse("perfil-consumidor")
    assert LojaFavoritas.objects.filter(id_usuario=usuario, id_loja=loja).exists()

    perfil = client_logado.get(reverse("perfil-consumidor"))
    assert [f.id_loja for f in perfil.context["loja_fav"]] == [loja]
    assert "Padaria Central" in perfil.content.decode()

@pytest.mark.django_db
def test_ct048_favoritar_volta_para_a_pagina_de_origem(client_logado, loja):
    origem = f"http://testserver/loja/{loja.id_loja}/"
    resposta = client_logado.post(reverse("favoritar-loja", args=[loja.id_loja]), HTTP_REFERER=origem)
    assert resposta.url == origem

@pytest.mark.django_db
def test_ct048_favoritar_de_novo_remove_dos_favoritos(client_logado, usuario, loja):
    client_logado.post(reverse("favoritar-loja", args=[loja.id_loja]))
    client_logado.post(reverse("favoritar-loja", args=[loja.id_loja]))
    assert not LojaFavoritas.objects.filter(id_usuario=usuario, id_loja=loja).exists()

@pytest.mark.django_db
def test_ct048_favoritar_exige_login(client, loja):
    resposta = client.post(reverse("favoritar-loja", args=[loja.id_loja]))
    assert resposta.url == reverse("login")
    assert not LojaFavoritas.objects.exists()

# ------------------------------- CT-049 ------------------------------------ #
@pytest.mark.django_db
def test_ct049_perfil_lista_apenas_as_lojas_favoritadas_pelo_usuario(client_logado, usuario, outro_usuario, loja, categorias):
    from AppStoreLink.models import Endereco, Loja
    outra = Loja.objects.create(
        nome_loja="Loja Alheia", email_loja="alheia@gmail.com", telefone_loja="11900000000", cnpj="00000000000100",
        id_endereco=Endereco.objects.create(rua="R", numero_estabelecimento="1", cep="01001000"),
        id_categoria=categorias["Moda"],
    )
    LojaFavoritas.objects.create(id_usuario=usuario, id_loja=loja)
    LojaFavoritas.objects.create(id_usuario=outro_usuario, id_loja=outra)

    perfil = client_logado.get(reverse("perfil-consumidor"))
    html = perfil.content.decode()

    assert [f.id_loja for f in perfil.context["loja_fav"]] == [loja]
    assert "Padaria Central" in html and "Loja Alheia" not in html

@pytest.mark.django_db
def test_ct049_sem_favoritas_mostra_mensagem_de_lista_vazia(client_logado):
    resposta = client_logado.get(reverse("perfil-consumidor"))
    assert list(resposta.context["loja_fav"]) == []                 # nenhuma loja favorita na lista
    assert "Procurar lojas" in resposta.content.decode()            # a tela oferece o botão para buscar lojas

# ------------------------------- CT-051 ------------------------------------ #
@pytest.mark.django_db
def test_ct051_model_aceita_foto_valida_e_guarda_com_nome_aleatorio(usuario, imagem):
    """A regra de foto já está ligada ao campo Usuario.foto (model + armazenamento de arquivos)."""
    usuario.foto = imagem("minha foto.png")
    usuario.full_clean()          # roda os validators do campo
    usuario.save()

    assert usuario.foto.name.startswith("usuarios/") and usuario.foto.name.endswith(".png")
    assert "minha" not in usuario.foto.name
    assert usuario.foto.storage.exists(usuario.foto.name)

@pytest.mark.django_db
def test_ct051_model_recusa_arquivo_que_nao_e_imagem(usuario):
    from django.core.exceptions import ValidationError
    from django.core.files.uploadedfile import SimpleUploadedFile
    usuario.foto = SimpleUploadedFile("falsa.jpg", b"texto")
    with pytest.raises(ValidationError):
        usuario.full_clean()

@pytest.mark.django_db
@pytest.mark.xfail(strict=True, reason=(
    "FUNCIONALIDADE NÃO IMPLEMENTADA: o formulário 'Salvar foto' envia o arquivo para perfil-consumidor, "
    "mas a view perfil_consumidor não trata POST (só exibe a página), então a foto nunca é gravada. "
    "O model e as regras de validação já existem (testados acima e em tests/unit)."
))
def test_ct051_enviar_foto_pelo_perfil_grava_a_foto_do_usuario(client_logado, usuario, imagem):
    client_logado.post(reverse("perfil-consumidor"), {"foto": imagem("perfil.png")})
    usuario.refresh_from_db()
    assert usuario.foto

DADOS_LOJA = {
    "nome_loja": "Mercado Bom Preço",
    "rua": "Praça da Sé",
    "numero": "50",
    "cep": "01001-000",
    "email_loja": "mercado@gmail.com",
    "telefone_loja": "11955554444",
    "cnpj": "11222333000144",
    "link_loja": "https://mercado.example.com",
    "categoria": "Alimentos",
}

# ------------------------------- CT-007 ------------------------------------ #
@pytest.mark.django_db
def test_ct007_cadastrar_loja_salva_loja_e_endereco(client_logado, categorias, viacep):
    resposta = client_logado.post(reverse("perfil-loja"), DADOS_LOJA)

    assert resposta.status_code == 302 and resposta.url == reverse("perfil-loja")
    assert any("cadastrada com sucesso" in m for m in mensagens(resposta))

    loja = Loja.objects.get(cnpj="11222333000144")
    assert loja.nome_loja == "Mercado Bom Preço"
    assert loja.email_loja == "mercado@gmail.com"
    assert loja.telefone_loja == "11955554444"
    assert loja.id_categoria.tipo_categoria == "Alimentos"
    assert loja.id_endereco.rua == "Praça da Sé"
    assert loja.id_endereco.numero_estabelecimento == "50"
    assert loja.id_endereco.cep == "01001000"      # gravado só com os 8 dígitos

@pytest.mark.django_db
def test_ct007_informacoes_cadastradas_aparecem_no_perfil(client_logado, categorias, viacep):
    client_logado.post(reverse("perfil-loja"), DADOS_LOJA)

    html = client_logado.get(reverse("perfil-loja")).content.decode()
    for texto in ("Mercado Bom Preço", "mercado@gmail.com", "11955554444", "11222333000144", "Praça da Sé"):
        assert texto in html

@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor, trecho", [
    ("email_loja", "mercado@exemplo.com", "serviço de email"),
    ("cnpj", "123", "14 números"),
    ("telefone_loja", "123", "11 números"),
    ("categoria", "Inexistente", "categoria válida"),
])
def test_ct007_dados_invalidos_nao_criam_loja(client_logado, categorias, viacep, campo, valor, trecho):
    resposta = client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, campo: valor})

    assert resposta.status_code == 200
    assert Loja.objects.count() == 0 and Endereco.objects.count() == 0
    assert any(trecho in m for m in mensagens(resposta))

@pytest.mark.django_db
def test_ct007_email_cnpj_e_telefone_repetidos_sao_recusados(client_logado, categorias, viacep, loja):
    for campo, valor in [("email_loja", loja.email_loja), ("cnpj", loja.cnpj), ("telefone_loja", loja.telefone_loja)]:
        resposta = client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, campo: valor})
        assert resposta.status_code == 200
        assert any(" já " in m or " ja " in m for m in mensagens(resposta))
    assert Loja.objects.count() == 1

# ------------------------------- CT-008 ------------------------------------ #
DADOS_EDICAO = {
    "nome_loja": "Padaria Nova Era", "rua": "Praça da Sé", "numero": "200", "cep": "01001000",
    "email_loja": "novaera@gmail.com", "telefone_loja": "11933334444",
    "cnpj": "99888777000166", "link_loja": "https://novaera.example.com", "categoria": "Moda",
}

@pytest.mark.django_db
def test_ct008_editar_loja_salva_as_alteracoes_e_mostra_os_dados_novos(client_logado, loja, viacep):
    resposta = client_logado.post(reverse("loja-editar", args=[loja.id_loja]), DADOS_EDICAO)

    assert resposta.status_code == 302
    assert resposta.url == reverse("InformacoesLoja", args=[loja.id_loja])

    loja.refresh_from_db()
    assert loja.nome_loja == "Padaria Nova Era"
    assert loja.email_loja == "novaera@gmail.com"
    assert loja.id_categoria.tipo_categoria == "Moda"
    assert loja.id_endereco.numero_estabelecimento == "200"
    assert Loja.objects.count() == 1                      # editou, não criou outra

    pagina = client_logado.get(resposta.url).content.decode()
    assert "Padaria Nova Era" in pagina

@pytest.mark.django_db
def test_ct008_editar_loja_exige_login(client, loja, viacep):
    resposta = client.post(reverse("loja-editar", args=[loja.id_loja]), DADOS_EDICAO)

    assert resposta.status_code == 302 and resposta.url == reverse("login")
    loja.refresh_from_db()
    assert loja.nome_loja == "Padaria Central"           # nada mudou

@pytest.mark.django_db
def test_ct008_edicao_invalida_nao_altera_a_loja(client_logado, loja, viacep):
    client_logado.post(reverse("loja-editar", args=[loja.id_loja]), {**DADOS_EDICAO, "cnpj": "123"})
    loja.refresh_from_db()
    assert loja.nome_loja == "Padaria Central" and loja.cnpj == "12345678000199"

@pytest.mark.django_db
def test_ct008_loja_inexistente_da_404(client_logado, viacep):
    assert client_logado.post(reverse("loja-editar", args=[9999]), DADOS_EDICAO).status_code == 404

# ------------------------------- CT-011 ------------------------------------ #
@pytest.mark.django_db
def test_ct011_cep_invalido_nao_cria_loja_e_avisa_o_usuario(client_logado, categorias, viacep):
    resposta = client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, "cep": "123"})

    assert resposta.status_code == 200
    assert Loja.objects.count() == 0 and Endereco.objects.count() == 0
    assert any("CEP inválido" in m for m in mensagens(resposta))

@pytest.mark.django_db
def test_ct011_cep_nao_encontrado_nao_cria_loja_e_avisa_o_usuario(client_logado, categorias, viacep):
    viacep(RespostaFalsa(200, {"erro": "true"}))
    resposta = client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, "cep": "99999999"})

    assert Loja.objects.count() == 0
    assert any("não existe" in m for m in mensagens(resposta))

@pytest.mark.django_db
def test_ct011_api_fora_do_ar_nao_cria_loja_e_avisa_o_usuario(client_logado, categorias, viacep):
    viacep(erro=requests.ConnectionError())
    resposta = client_logado.post(reverse("perfil-loja"), DADOS_LOJA)

    assert Loja.objects.count() == 0
    assert any("Tente novamente" in m for m in mensagens(resposta))

@pytest.mark.django_db
@pytest.mark.parametrize("cep, resposta_api, status_esperado, trecho", [
    ("01001000", RespostaFalsa(200, {"logradouro": "Praça da Sé", "localidade": "São Paulo", "uf": "SP"}), 200, None),
    ("123", None, 400, "CEP inválido"),
    ("99999999", RespostaFalsa(200, {"erro": "true"}), 404, "não existe"),
    ("01001000", RespostaFalsa(500, {}), 503, "Tente novamente"),
])
def test_ct010_ct011_endpoint_api_cep_responde_o_status_certo(client, viacep, cep, resposta_api, status_esperado, trecho):
    """É este endpoint JSON que a tela do perfil da loja chama para preencher o endereço."""
    if resposta_api is not None:
        viacep(resposta_api)
    resposta = client.get(reverse("api-cep", args=[cep]))

    assert resposta.status_code == status_esperado
    if status_esperado == 200:
        assert resposta.json()["rua"] == "Praça da Sé"
    else:
        assert trecho in resposta.json()["erro"]

@pytest.mark.django_db
def test_ct010_endpoint_api_cep_so_aceita_get(client):
    assert client.post(reverse("api-cep", args=["01001000"])).status_code == 405

# ------------------------------- CT-012 ------------------------------------ #
@pytest.mark.django_db
@pytest.mark.parametrize("categoria", CATEGORIAS)
def test_ct012_cada_categoria_disponivel_pode_ser_escolhida_e_e_salva(client_logado, categorias, viacep, categoria):
    client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, "categoria": categoria})

    assert Loja.objects.get().id_categoria.tipo_categoria == categoria

@pytest.mark.django_db
def test_ct012_categoria_escolhida_permanece_no_perfil(client_logado, categorias, viacep):
    client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, "categoria": "Pets"})
    html = client_logado.get(reverse("perfil-loja")).content.decode()
    assert 'id="categoria-input"' in html and 'value="Pets"' in html

# ------------------------------- CT-013 ------------------------------------ #
@pytest.mark.django_db
def test_ct013_foto_da_loja_enviada_fica_associada_a_loja(client_logado, categorias, viacep, imagem):
    client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, "foto_estabelecimento": imagem("loja.png")})
    assert Loja.objects.get().foto_estabelecimento

# ------------------------------- CT-016 ------------------------------------ #
@pytest.mark.django_db
def test_ct016_excluir_loja_apaga_loja_endereco_e_dados_ligados(
    client_logado, loja, produto, servico, usuario, outro_usuario
):
    LojaFavoritas.objects.create(id_usuario=usuario, id_loja=loja)
    Avaliacao.objects.create(nota=5, comentario="ótima", id_usuario=outro_usuario, id_loja=loja)
    id_endereco = loja.id_endereco_id

    resposta = client_logado.post(reverse("loja-excluir", args=[loja.id_loja]))

    assert resposta.status_code == 302 and resposta.url == reverse("perfil-loja")
    assert any("foi excluída" in m for m in mensagens(resposta))
    assert not Loja.objects.exists()
    assert not Endereco.objects.filter(pk=id_endereco).exists()    # endereço órfão removido
    assert not Produto.objects.exists() and not Servico.objects.exists()
    assert not LojaFavoritas.objects.exists() and not Avaliacao.objects.exists()

@pytest.mark.django_db
def test_ct016_depois_de_excluir_o_perfil_deixa_de_mostrar_a_loja(client_logado, loja):
    client_logado.post(reverse("loja-excluir", args=[loja.id_loja]))
    resposta = client_logado.get(reverse("perfil-loja"))
    assert resposta.context["loja"] is None
    assert 'value="Padaria Central"' not in resposta.content.decode()   # o campo Nome não vem mais preenchido

@pytest.mark.django_db
def test_ct016_excluir_so_aceita_post(client_logado, loja):
    assert client_logado.get(reverse("loja-excluir", args=[loja.id_loja])).status_code == 405
    assert Loja.objects.count() == 1

@pytest.mark.django_db
def test_ct016_visitante_sem_login_nao_pode_excluir_loja(client, loja):
    client.post(reverse("loja-excluir", args=[loja.id_loja]))
    assert Loja.objects.filter(pk=loja.pk).exists()

# ------------------------------- CT-018 ------------------------------------ #
@pytest.mark.django_db
@pytest.mark.parametrize("campo_vazio", [
    "cep", "email_loja", "telefone_loja", "cnpj", "categoria", "nome_loja", "rua", "numero",
])
def test_ct018_loja_com_campo_obrigatorio_vazio_nao_e_salva(client_logado, categorias, viacep, campo_vazio):
    resposta = client_logado.post(reverse("perfil-loja"), {**DADOS_LOJA, campo_vazio: ""})

    assert Loja.objects.count() == 0, f"a loja foi salva com '{campo_vazio}' vazio"
    assert mensagens(resposta)          # o usuário é avisado do problema

ROTAS_CATEGORIA = {
    "Alimentos": "CatAlimentos", "Moda": "CatModa", "Esportes": "CatEsportes",
    "Construção": "CatConstrucao", "Saúde": "CatSaude", "Pets": "CatPets",
    "Ambiente": "CatAmbiente", "Tecnologia": "CatTecnologia", "Beleza": "CatBeleza",
    "Outros": "CatOutros",
}

# ------------------------------- CT-004 ------------------------------------ #
def test_ct004_as_10_categorias_previstas_existem_no_teste():
    assert sorted(ROTAS_CATEGORIA) == sorted(CATEGORIAS) and len(CATEGORIAS) == 10

@pytest.mark.django_db
@pytest.mark.parametrize("nome, rota", ROTAS_CATEGORIA.items())
def test_ct004_barra_lateral_exibe_cada_categoria_com_o_link_certo(client, nome, rota):
    html = client.get(reverse("index")).content.decode()
    padrao = rf'<a[^>]*class="cat-btn [^"]*"[^>]*href="{re.escape(reverse(rota))}"[^>]*>(?:(?!</a>).)*{nome}'
    assert re.search(padrao, html, re.S), f"categoria {nome} não aparece na barra lateral"

@pytest.mark.django_db
def test_ct004_barra_lateral_tem_exatamente_10_categorias(client):
    html = client.get(reverse("index")).content.decode()
    assert len(re.findall(r'class="cat-btn ', html)) == 10

@pytest.mark.django_db
@pytest.mark.parametrize("nome, rota", ROTAS_CATEGORIA.items())
def test_ct004_pagina_da_categoria_lista_so_lojas_dela(client, loja, categorias, nome, rota):
    """Complemento: clicar na categoria abre uma página que só mostra lojas daquela categoria."""
    resposta = client.get(reverse(rota))
    assert resposta.status_code == 200
    nomes = [l.nome_loja for l in resposta.context["lojas"]]
    assert ("Padaria Central" in nomes) == (nome == "Alimentos")

# ------------------------------- CT-006 ------------------------------------ #
@pytest.mark.django_db
def test_ct006_inicio_tem_botao_sua_loja_apontando_para_o_perfil_da_loja(client):
    html = client.get(reverse("index")).content.decode()
    padrao = rf'href="{re.escape(reverse("perfil-loja"))}"[^>]*>(?:(?!</a>).)*Sua loja'
    assert re.search(padrao, html, re.S | re.I)

@pytest.mark.django_db
def test_ct006_usuario_autenticado_ve_a_tela_de_gerenciamento_da_loja(client_logado):
    resposta = client_logado.get(reverse("perfil-loja"))
    html = resposta.content.decode()

    assert resposta.status_code == 200
    assert 'id="formLoja"' in html          # formulário para criar/editar a loja
    assert "Salvar Loja" in html
    assert "Para criar sua loja você precisa fazer login" not in html

@pytest.mark.django_db
def test_ct006_loja_ja_cadastrada_aparece_para_ser_gerenciada(client_logado, loja):
    resposta = client_logado.get(reverse("perfil-loja"))
    html = resposta.content.decode()

    assert resposta.context["loja"] == loja
    assert "Padaria Central" in html
    assert "Excluir loja" in html

@pytest.mark.django_db
def test_ct006_visitante_nao_autenticado_e_enviado_para_o_login(client):
    resposta = client.get(reverse("perfil-loja"))

    assert resposta.status_code == 302 and resposta.url == reverse("login")
    assert any("precisa fazer login" in m for m in mensagens(resposta))

# ------------------------------- CT-045 ------------------------------------ #
@pytest.mark.django_db
def test_ct045_tela_de_suporte_exibe_o_email_oficial(client):
    resposta = client.get(reverse("suporte"))
    html = resposta.content.decode()

    assert resposta.status_code == 200
    assert "StoreLinkOficialSuporte@gmail.com" in html
    assert 'href="mailto:StoreLinkOficialSuporte@gmail.com"' in html

# ------------------------------- CT-046 ------------------------------------ #
def _imagens_do_tutorial(client):
    html = client.get(reverse("tutorial")).content.decode()
    # o Django escreve o espaço do nome do arquivo como %20 na URL
    numeros = re.findall(r"/static/AppStoreLink/images/tutorial(?:%20| )(\d+)\.png", html)
    return [f"tutorial {n}.png" for n in numeros]

@pytest.mark.django_db
def test_ct046_tutorial_mostra_8_fotos_na_ordem_prevista(client):
    assert _imagens_do_tutorial(client) == [f"tutorial {n}.png" for n in range(1, 9)]

@pytest.mark.django_db
def test_ct046_todos_os_arquivos_de_foto_do_tutorial_existem(client):
    ausentes = [nome for nome in _imagens_do_tutorial(client)
                if finders.find(f"AppStoreLink/images/{nome}") is None]
    assert ausentes == []

REFERER_PRODUTOS = {"HTTP_REFERER": "http://testserver/produtos-loja/"}

def dados_produto(categorias, **extra):
    return {
        "nome_produto": "Bolo de Cenoura", "preco_produto": "12,50",
        "descricao_produto": "Com cobertura de chocolate",
        "id_categoria": str(categorias["Alimentos"].id_categoria), **extra,
    }

# ------------------------------- CT-019 ------------------------------------ #
@pytest.mark.django_db
def test_ct019_adicionar_produto_salva_e_aparece_na_lista_da_loja(client_logado, loja, categorias):
    resposta = client_logado.post(reverse("produto-criar"), dados_produto(categorias))

    assert resposta.status_code == 302 and resposta.url == reverse("produtos-loja")
    assert any("cadastrado com sucesso" in m for m in mensagens(resposta))

    produto = Produto.objects.get(nome_produto="Bolo de Cenoura")
    assert produto.preco == Decimal("12.50")          # vírgula virou ponto
    assert produto.descricao == "Com cobertura de chocolate"
    assert produto.id_loja == loja

    pagina = client_logado.get(reverse("produtos-loja"))
    assert produto in pagina.context["produtos"]
    assert "Bolo de Cenoura" in pagina.content.decode()

@pytest.mark.django_db
def test_ct019_descricao_vazia_e_gravada_como_nula(client_logado, loja, categorias):
    client_logado.post(reverse("produto-criar"), dados_produto(categorias, descricao_produto=""))
    assert Produto.objects.get().descricao is None

@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor, trecho", [
    ("nome_produto", "", "nome do produto é obrigatório"),
    ("preco_produto", "abc", "preço válido"),
    ("preco_produto", "0", "maior que zero"),
    ("preco_produto", "-3", "maior que zero"),
    ("id_categoria", "9999", "categoria válida"),
    ("id_categoria", "", "categoria válida"),
])
def test_ct019_dados_invalidos_nao_cadastram_produto(client_logado, loja, categorias, campo, valor, trecho):
    resposta = client_logado.post(reverse("produto-criar"), dados_produto(categorias, **{campo: valor}))

    assert resposta.status_code == 302
    assert Produto.objects.count() == 0
    assert any(trecho in m for m in mensagens(resposta))

@pytest.mark.django_db
def test_ct019_sem_loja_cadastrada_nao_cadastra_produto(client_logado, categorias):
    resposta = client_logado.post(reverse("produto-criar"), dados_produto(categorias))
    assert Produto.objects.count() == 0
    assert any("Cadastre uma loja" in m for m in mensagens(resposta))

@pytest.mark.django_db
def test_ct019_visitante_sem_login_nao_pode_cadastrar_produto(client, loja, categorias):
    client.post(reverse("produto-criar"), dados_produto(categorias))
    assert Produto.objects.count() == 0

# ------------------------------- CT-020 ------------------------------------ #
@pytest.mark.django_db
def test_ct020_editar_produto_salva_as_alteracoes(client_logado, produto):
    resposta = client_logado.post(reverse("produto-editar", args=[produto.id_produto]), {
        "nome_produto": "Pão de Queijo", "preco_produto": "3,75", "descricao_produto": "Mineiro",
    }, **REFERER_PRODUTOS)

    assert resposta.status_code == 302 and resposta.url == "http://testserver/produtos-loja/"
    produto.refresh_from_db()
    assert (produto.nome_produto, produto.preco, produto.descricao) == ("Pão de Queijo", Decimal("3.75"), "Mineiro")
    assert Produto.objects.count() == 1
    assert "Pão de Queijo" in client_logado.get(reverse("produtos-loja")).content.decode()

@pytest.mark.django_db
def test_ct020_edicao_invalida_nao_altera_o_produto(client_logado, produto):
    resposta = client_logado.post(reverse("produto-editar", args=[produto.id_produto]), {
        "nome_produto": "", "preco_produto": "abc", "descricao_produto": "x",
    }, **REFERER_PRODUTOS)

    produto.refresh_from_db()
    assert produto.nome_produto == "Pão Francês" and produto.preco == Decimal("1.50")
    assert len(mensagens(resposta)) == 2

@pytest.mark.django_db
def test_ct020_redirecionamento_ignora_site_de_fora(client_logado, produto):
    """_voltar() só aceita voltar para o próprio site (proteção contra 'open redirect')."""
    resposta = client_logado.post(
        reverse("produto-editar", args=[produto.id_produto]),
        {"nome_produto": "X", "preco_produto": "1"}, HTTP_REFERER="http://site-malicioso.com/",
    )
    assert resposta.url == reverse("index")

# ------------------------------- CT-021 ------------------------------------ #
@pytest.mark.django_db
def test_ct021_excluir_produto_remove_da_lista(client_logado, produto):
    resposta = client_logado.post(reverse("produto-excluir", args=[produto.id_produto]), **REFERER_PRODUTOS)

    assert resposta.status_code == 302
    assert any('"Pão Francês" foi excluído' in m for m in mensagens(resposta))
    assert not Produto.objects.filter(pk=produto.pk).exists()
    assert produto not in client_logado.get(reverse("produtos-loja")).context["produtos"]

@pytest.mark.django_db
def test_ct021_excluir_exige_login(client, produto):
    resposta = client.post(reverse("produto-excluir", args=[produto.id_produto]))
    assert resposta.url == reverse("login")
    assert Produto.objects.filter(pk=produto.pk).exists()

@pytest.mark.django_db
def test_ct021_excluir_produto_que_nao_existe_mais_devolve_404(client_logado):
    resposta = client_logado.post(reverse("produto-excluir", args=[9999]), **REFERER_PRODUTOS)
    assert resposta.status_code == 404

DADOS_SERVICO = {"nome_servico": "Corte de Cabelo", "preco": "45,00", "descricao": "Corte masculino"}

# ------------------------------- CT-022 ------------------------------------ #
@pytest.mark.django_db
def test_ct022_adicionar_servico_salva_e_aparece_na_lista(client_logado, loja):
    resposta = client_logado.post(reverse("servicos-loja"), DADOS_SERVICO)

    assert resposta.status_code == 302 and resposta.url == reverse("servicos-loja")
    servico = Servico.objects.get(nome_servico="Corte de Cabelo")
    assert servico.preco == Decimal("45.00") and servico.id_loja == loja

    pagina = client_logado.get(reverse("servicos-loja"))
    assert servico in pagina.context["servicos"]
    assert "Corte de Cabelo" in pagina.content.decode()

@pytest.mark.django_db
@pytest.mark.parametrize("campo, valor, trecho", [
    ("nome_servico", "", "nome do serviço é obrigatório"),
    ("nome_servico", "a" * 101, "no máximo 100"),
    ("preco", "abc", "preço válido"),
    ("preco", "0", "maior que zero"),
])
def test_ct022_dados_invalidos_nao_cadastram_servico(client_logado, loja, campo, valor, trecho):
    resposta = client_logado.post(reverse("servicos-loja"), {**DADOS_SERVICO, campo: valor})

    assert resposta.status_code == 200                # recarrega a página mostrando os erros
    assert Servico.objects.count() == 0
    assert any(trecho in m for m in mensagens(resposta))

@pytest.mark.django_db
def test_ct022_sem_loja_cadastrada_nao_cadastra_servico(client_logado):
    resposta = client_logado.post(reverse("servicos-loja"), DADOS_SERVICO)
    assert Servico.objects.count() == 0
    assert any("Cadastre uma loja" in m for m in mensagens(resposta))

# ------------------------------- CT-023 ------------------------------------ #
@pytest.mark.django_db
def test_ct023_editar_servico_salva_as_alteracoes(client_logado, servico):
    resposta = client_logado.post(reverse("servico-editar", args=[servico.id_servico]), {
        "nome_servico": "Entrega Super Rápida", "preco": "14,90", "descricao": "Em 15 minutos",
    })

    assert resposta.status_code == 302
    assert resposta.url == reverse("InformacoesServico", args=[servico.id_loja_id])
    servico.refresh_from_db()
    assert (servico.nome_servico, servico.preco, servico.descricao) == (
        "Entrega Super Rápida", Decimal("14.90"), "Em 15 minutos")
    assert "Entrega Super Rápida" in client_logado.get(resposta.url).content.decode()

@pytest.mark.django_db
def test_ct023_editar_servico_exige_login(client, servico):
    resposta = client.post(reverse("servico-editar", args=[servico.id_servico]), {"nome_servico": "X", "preco": "1"})
    assert resposta.url == reverse("login")
    servico.refresh_from_db()
    assert servico.nome_servico == "Entrega Express"

@pytest.mark.django_db
def test_ct023_edicao_invalida_mostra_erro_sem_quebrar(client_logado, servico):
    resposta = client_logado.post(reverse("servico-editar", args=[servico.id_servico]), {"nome_servico": "", "preco": "abc"})
    assert resposta.status_code == 302
    servico.refresh_from_db()
    assert servico.nome_servico == "Entrega Express"

# ------------------------------- CT-024 ------------------------------------ #
@pytest.mark.django_db
def test_ct024_excluir_servico_remove_da_lista(client_logado, servico):
    resposta = client_logado.post(reverse("servico-excluir", args=[servico.id_servico]))

    assert resposta.status_code == 302
    assert resposta.url == reverse("InformacoesServico", args=[servico.id_loja_id])
    assert any('"Entrega Express" foi excluído' in m for m in mensagens(resposta))
    assert not Servico.objects.exists()
    assert servico not in client_logado.get(reverse("servicos-loja")).context["servicos"]

@pytest.mark.django_db
def test_ct024_excluir_servico_exige_login(client, servico):
    resposta = client.post(reverse("servico-excluir", args=[servico.id_servico]))
    assert resposta.url == reverse("login")
    assert Servico.objects.exists()

@pytest.mark.django_db
def test_ct024_excluir_servico_inexistente_da_404(client_logado):
    assert client_logado.post(reverse("servico-excluir", args=[9999])).status_code == 404
    
# ===================== CT-058 a CT-065 — Verificação de DONO ===================== #
@pytest.fixture
def loja_do_dono(loja, usuario):
    """Loja pertencente à Maria (a mesma que está logada em `client_logado`)."""
    loja.id_dono = usuario
    loja.save()
    return loja

@pytest.fixture
def loja_alheia(loja, outro_usuario):
    """Loja pertencente ao João: a Maria (logada) NÃO é a dona."""
    loja.id_dono = outro_usuario
    loja.save()
    return loja

# ------------------------------- CT-058 ------------------------------------ #
@pytest.mark.django_db
def test_ct058_dono_edita_a_propria_loja(client_logado, usuario, loja_do_dono, viacep):
    assert loja_do_dono.id_dono_id == usuario.pk          # pré-condição: é dono de verdade

    resposta = client_logado.post(reverse("loja-editar", args=[loja_do_dono.id_loja]), DADOS_EDICAO)

    assert resposta.status_code == 302
    assert resposta.url == reverse("InformacoesLoja", args=[loja_do_dono.id_loja])
    loja_do_dono.refresh_from_db()
    assert loja_do_dono.nome_loja == "Padaria Nova Era"
    assert Loja.objects.count() == 1                                # editou, não criou outra

@pytest.mark.django_db
def test_ct058_dono_exclui_a_propria_loja(client_logado, usuario, loja_do_dono):
    assert loja_do_dono.id_dono_id == usuario.pk

    resposta = client_logado.post(reverse("loja-excluir", args=[loja_do_dono.id_loja]))

    assert resposta.status_code == 302 and resposta.url == reverse("perfil-loja")
    assert any("foi excluída" in m for m in mensagens(resposta))
    assert not Loja.objects.exists()

# ------------------------------- CT-059 ------------------------------------ #
@pytest.mark.django_db
def test_ct059_dono_edita_o_proprio_produto(client_logado, usuario, loja_do_dono, produto):
    assert produto.id_loja.id_dono_id == usuario.pk

    resposta = client_logado.post(reverse("produto-editar", args=[produto.id_produto]), {
        "nome_produto": "Pão de Queijo", "preco_produto": "3,75", "descricao_produto": "Mineiro",
    }, **REFERER_PRODUTOS)

    assert resposta.status_code == 302
    assert any("atualizado com sucesso" in m for m in mensagens(resposta))
    produto.refresh_from_db()
    assert (produto.nome_produto, produto.preco, produto.descricao) == ("Pão de Queijo", Decimal("3.75"), "Mineiro")

@pytest.mark.django_db
def test_ct059_dono_exclui_o_proprio_produto(client_logado, usuario, loja_do_dono, produto):
    resposta = client_logado.post(reverse("produto-excluir", args=[produto.id_produto]), **REFERER_PRODUTOS)

    assert resposta.status_code == 302
    assert any('"Pão Francês" foi excluído' in m for m in mensagens(resposta))
    assert not Produto.objects.filter(pk=produto.pk).exists()

# ------------------------------- CT-060 ------------------------------------ #
@pytest.mark.django_db
def test_ct060_dono_edita_o_proprio_servico(client_logado, usuario, loja_do_dono, servico):
    assert servico.id_loja.id_dono_id == usuario.pk

    resposta = client_logado.post(reverse("servico-editar", args=[servico.id_servico]), {
        "nome_servico": "Entrega Super Rápida", "preco": "14,90", "descricao": "Em 15 minutos",
    })

    assert resposta.status_code == 302
    assert resposta.url == reverse("InformacoesServico", args=[servico.id_loja_id])
    servico.refresh_from_db()
    assert (servico.nome_servico, servico.preco) == ("Entrega Super Rápida", Decimal("14.90"))

@pytest.mark.django_db
def test_ct060_dono_exclui_o_proprio_servico(client_logado, usuario, loja_do_dono, servico):
    resposta = client_logado.post(reverse("servico-excluir", args=[servico.id_servico]))

    assert resposta.status_code == 302
    assert resposta.url == reverse("InformacoesServico", args=[servico.id_loja_id])
    assert any('"Entrega Express" foi excluído' in m for m in mensagens(resposta))
    assert not Servico.objects.exists()

# ------------------------------- CT-061 ------------------------------------ #
@pytest.mark.django_db
def test_ct061_dono_edita_o_proprio_comentario(client_logado, usuario, loja):
    Avaliacao.objects.create(nota=3, comentario="Atendimento razoável", id_usuario=usuario, id_loja=loja)
    original = Avaliacao.objects.get()

    avaliar_loja(client_logado, loja, 5, "Mudei de ideia: excelente!")

    assert Avaliacao.objects.count() == 1                           # editou, não criou outro
    editado = Avaliacao.objects.get()
    assert editado.pk == original.pk and editado.id_usuario == usuario
    assert (editado.nota, editado.comentario) == (5, "Mudei de ideia: excelente!")

@pytest.mark.django_db
def test_ct061_dono_exclui_o_proprio_comentario(client_logado, usuario, loja):
    av = Avaliacao.objects.create(nota=4, comentario="Bom", id_usuario=usuario, id_loja=loja)

    resposta = client_logado.post(reverse("avaliacao-excluir", args=[av.pk]))   # hoje: NoReverseMatch

    assert resposta.status_code == 302
    assert not Avaliacao.objects.filter(pk=av.pk).exists()

# ------------------------------- CT-062 ------------------------------------ #
@pytest.mark.django_db
def test_ct062_nao_dono_nao_consegue_editar_a_loja_e_recebe_404(client_logado, loja_alheia, viacep):
    resposta = client_logado.post(reverse("loja-editar", args=[loja_alheia.id_loja]), DADOS_EDICAO)

    loja_alheia.refresh_from_db()
    assert loja_alheia.nome_loja == "Padaria Central"               # nada mudou
    assert resposta.status_code == 404

@pytest.mark.django_db
def test_ct062_nao_dono_nao_consegue_excluir_a_loja_e_recebe_404(client_logado, loja_alheia):
    resposta = client_logado.post(reverse("loja-excluir", args=[loja_alheia.id_loja]))

    assert Loja.objects.filter(pk=loja_alheia.pk).exists()          # continua existindo
    assert resposta.status_code == 404

# ------------------------------- CT-063 ------------------------------------ #
@pytest.mark.django_db
def test_ct063_nao_dono_nao_consegue_editar_o_produto_e_recebe_404(client_logado, loja_alheia, produto):
    resposta = client_logado.post(reverse("produto-editar", args=[produto.id_produto]), {
        "nome_produto": "Invadido", "preco_produto": "99", "descricao_produto": "x",
    }, **REFERER_PRODUTOS)

    produto.refresh_from_db()
    assert (produto.nome_produto, produto.preco) == ("Pão Francês", Decimal("1.50"))
    assert resposta.status_code == 404

@pytest.mark.django_db
def test_ct063_nao_dono_nao_consegue_excluir_o_produto_e_recebe_404(client_logado, loja_alheia, produto):
    resposta = client_logado.post(reverse("produto-excluir", args=[produto.id_produto]), **REFERER_PRODUTOS)

    assert Produto.objects.filter(pk=produto.pk).exists()
    assert resposta.status_code == 404

# ------------------------------- CT-064 ------------------------------------ #
@pytest.mark.django_db
def test_ct064_nao_dono_nao_consegue_editar_o_servico_e_recebe_404(client_logado, loja_alheia, servico):
    resposta = client_logado.post(reverse("servico-editar", args=[servico.id_servico]), {
        "nome_servico": "Invadido", "preco": "99", "descricao": "x",
    })

    servico.refresh_from_db()
    assert (servico.nome_servico, servico.preco) == ("Entrega Express", Decimal("9.90"))
    assert resposta.status_code == 404

@pytest.mark.django_db
def test_ct064_nao_dono_nao_consegue_excluir_o_servico_e_recebe_404(client_logado, loja_alheia, servico):
    resposta = client_logado.post(reverse("servico-excluir", args=[servico.id_servico]))

    assert Servico.objects.filter(pk=servico.pk).exists()
    assert resposta.status_code == 404

# ------------------------------- CT-065 ------------------------------------ #
@pytest.mark.django_db
def test_ct065_nao_dono_do_comentario_nao_altera_o_comentario_de_outro_usuario(client_logado, usuario, outro_usuario, loja):
    """A Maria (logada) envia o formulário de avaliação: o comentário do João não pode ser tocado."""
    do_joao = Avaliacao.objects.create(nota=2, comentario="Comentário do João", id_usuario=outro_usuario, id_loja=loja)

    avaliar_loja(client_logado, loja, 5, "A Maria tentando sobrescrever")

    do_joao.refresh_from_db()
    assert (do_joao.nota, do_joao.comentario) == (2, "Comentário do João")      # intacto
    assert Avaliacao.objects.filter(id_loja=loja).count() == 2                  # a Maria criou o PRÓPRIO comentário
    assert Avaliacao.objects.get(id_usuario=usuario).comentario == "A Maria tentando sobrescrever"

@pytest.mark.django_db
@pytest.mark.parametrize("rota, id_inexistente", [
    ("avaliar-loja", 9999), ("avaliar-produto", 9999), ("avaliar-servico", 9999),
])
def test_ct065_get_object_or_404_item_inexistente_devolve_404(client_logado, rota, id_inexistente):
    resposta = client_logado.post(reverse(rota, args=[id_inexistente]), {"nota": 5, "comentario": "x"})
    assert resposta.status_code == 404
    assert not Avaliacao.objects.exists()

@pytest.mark.django_db
def test_ct065_get_object_or_404_sessao_de_usuario_inexistente_devolve_404(client, loja):
    sessao = client.session
    sessao["usuario_id"] = 9999                                    # sessão apontando para quem não existe
    sessao.save()

    resposta = avaliar_loja(client, loja, 5, "x")

    assert resposta.status_code == 404
    assert not Avaliacao.objects.exists()

@pytest.mark.django_db
def test_ct065_nao_dono_nao_consegue_excluir_comentario_de_outro_e_recebe_404(client_logado, outro_usuario, loja):
    do_joao = Avaliacao.objects.create(nota=2, comentario="Comentário do João", id_usuario=outro_usuario, id_loja=loja)

    resposta = client_logado.post(reverse("avaliacao-excluir", args=[do_joao.pk]))   # hoje: NoReverseMatch

    assert Avaliacao.objects.filter(pk=do_joao.pk).exists()
    assert resposta.status_code == 404


# ====== Testes pela INTERFACE (navegador real - Playwright) - antes em test_automatizados ====== #
# Abrem o site de verdade (live_server + Chromium): tela + view + banco funcionando juntos.
# Os ajudantes `ir` e `entrar` estão em tests/integration/conftest.py.
def pesquisar(page, live_server, termo):
    page.goto(live_server.url + "/")
    page.fill('input[name="q"]', termo)
    page.click("button.search-icon-btn") # botão "Buscar"

# ------------------------------- CT-031 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct031_pesquisar_loja_pelo_nome_mostra_a_loja(page, live_server, loja):
    pesquisar(page, live_server, "Padaria Central")

    expect(page).to_have_url(re.compile(r"/buscar/\?q=Padaria\+Central"))
    expect(page.get_by_role("heading", name='Resultados para "Padaria Central"')).to_be_visible()
    expect(page.locator(f'[data-url="/loja/{loja.id_loja}/"]')).to_contain_text("Padaria Central")

# ------------------------------- CT-032 / CT-033 ---------------------------- #
@pytest.mark.django_db(transaction=True)
def test_ct032_pesquisar_produto_mostra_o_produto(page, live_server, produto):
    pesquisar(page, live_server, "Pão Francês")

    expect(page).to_have_url(re.compile(r"/buscar/"))
    expect(page.locator(f'[data-url="/loja/{produto.id_loja_id}/produtos/"]')).to_contain_text("Pão Francês")

@pytest.mark.django_db(transaction=True)
def test_ct033_pesquisar_servico_mostra_o_servico(page, live_server, servico):
    pesquisar(page, live_server, "Entrega Express")

    expect(page).to_have_url(re.compile(r"/buscar/"))
    expect(page.locator(f'[data-url="/loja/{servico.id_loja_id}/servicos/"]')).to_contain_text("Entrega Express")

# ------------------------------- CT-034 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct034_termo_sem_resultado_mostra_mensagem_e_nenhum_cartao(page, live_server, loja, produto, servico):
    pesquisar(page, live_server, "zzzxxyyqq")

    expect(page).to_have_url(re.compile(r"/buscar/"))
    expect(page.get_by_text("Nenhum resultado encontrado")).to_be_visible()
    expect(page.get_by_text("Padaria Central")).to_have_count(0)
    expect(page.get_by_text("Pão Francês")).to_have_count(0)

# ------------------------------- CT-035 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct035_clicar_na_loja_do_resultado_abre_a_tela_da_loja(page, live_server, loja):
    pesquisar(page, live_server, "Padaria Central")

    page.locator(f'[data-url="/loja/{loja.id_loja}/"]').click()

    expect(page).to_have_url(live_server.url + f"/loja/{loja.id_loja}/")
    expect(page.get_by_text("Padaria Central").first).to_be_visible()

# ------------------------------- CT-036 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct036_clicar_no_produto_do_resultado_abre_a_tela_do_produto(page, live_server, produto):
    pesquisar(page, live_server, "Pão Francês")

    page.locator(f'[data-url="/loja/{produto.id_loja_id}/produtos/"]').click()

    expect(page).to_have_url(live_server.url + f"/loja/{produto.id_loja_id}/produtos/")
    expect(page.get_by_text("Pão Francês").first).to_be_visible()

# ------------------------------- CT-037 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct037_clicar_no_servico_do_resultado_abre_a_tela_do_servico(page, live_server, servico):
    pesquisar(page, live_server, "Entrega Express")

    page.locator(f'[data-url="/loja/{servico.id_loja_id}/servicos/"]').click()

    expect(page).to_have_url(live_server.url + f"/loja/{servico.id_loja_id}/servicos/")
    expect(page.get_by_text("Entrega Express").first).to_be_visible()

@pytest.mark.django_db(transaction=True)
def test_ct010_cep_valido_preenche_a_rua_e_leva_o_foco_para_o_numero(page, live_server, usuario, loja, entrar, viacep):
    entrar(usuario)
    page.goto(live_server.url + "/perfil-loja/")
    campo_rua = page.locator('input[name="rua"]')
    campo_rua.fill("")                                   # começa vazio

    page.fill('input[name="cep"]', "01001-000")
    page.locator('input[name="cep"]').blur()             # sair do campo dispara a consulta

    expect(campo_rua).to_have_value("Praça da Sé")
    expect(page.locator('input[name="numero"]')).to_be_focused()


@pytest.mark.django_db(transaction=True)
def test_ct011_cep_nao_encontrado_avisa_o_usuario_e_nao_preenche_a_rua(page, live_server, usuario, loja, entrar, viacep):
    viacep(RespostaFalsa(200, {"erro": "true"}))
    entrar(usuario)
    page.goto(live_server.url + "/perfil-loja/")
    campo_rua = page.locator('input[name="rua"]')
    campo_rua.fill("")
    avisos = []
    page.on("dialog", lambda d: (avisos.append(d.message), d.accept()))   # o site usa alert()

    page.fill('input[name="cep"]', "99999-999")
    page.locator('input[name="cep"]').blur()
    page.wait_for_timeout(500)

    assert avisos == ["Este CEP não existe."]
    expect(campo_rua).to_have_value("")

@pytest.mark.django_db(transaction=True)
def test_ct007_ct012_usuario_cadastra_loja_escolhendo_categoria(page, live_server, usuario, categorias, entrar, viacep):
    entrar(usuario)
    page.goto(live_server.url + "/perfil-loja/")

    page.fill('input[name="nome_loja"]', "Boutique Aurora")
    page.fill('input[name="cep"]', "01001-000")
    page.locator('input[name="cep"]').blur()
    expect(page.locator('input[name="rua"]')).to_have_value("Praça da Sé")   # CT-010 em ação
    page.fill('input[name="numero"]', "77")
    page.fill('input[name="email_loja"]', "aurora@gmail.com")
    page.fill('input[name="telefone_loja"]', "11977776666")
    page.fill('input[name="cnpj"]', "55444333000122")

    page.click("#classifBtn")                                                   # abre a lista de categorias
    page.locator(".perfil-classif-option", has_text="Moda").click()             # CT-012
    expect(page.locator("#classifName")).to_have_text("Moda")

    page.get_by_role("button", name="Salvar Loja").click()
    page.wait_for_url("**/perfil-loja/")

    loja = Loja.objects.get(cnpj="55444333000122")
    assert loja.nome_loja == "Boutique Aurora"
    assert loja.id_categoria.tipo_categoria == "Moda"
    expect(page.locator('input[name="nome_loja"]')).to_have_value("Boutique Aurora")   # aparece no perfil


@pytest.mark.django_db(transaction=True)
def test_ct038_ct040_usuario_avalia_a_loja_e_o_comentario_permanece_apos_atualizar(page, live_server, usuario, loja, entrar):
    entrar(usuario)
    page.goto(live_server.url + f"/loja/{loja.id_loja}/")

    page.locator('label[for="estrela5"]').click()                               # 5 estrelas
    page.fill("#comentario-loja", "Ótimo atendimento e produtos de qualidade.")
    page.get_by_role("button", name="ENVIAR COMENTÁRIO").click()

    texto = page.locator("article.info-comentario-card p", has_text="Ótimo atendimento e produtos de qualidade.")
    expect(texto).to_be_visible()                                               # aparece na lista
    avaliacao = Avaliacao.objects.get()
    assert (avaliacao.nota, avaliacao.id_usuario, avaliacao.id_loja) == (5, usuario, loja)

    page.reload()                                                               # CT-040: atualizar a página
    expect(texto).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_ct039_sem_estrelas_o_navegador_nao_deixa_enviar(page, live_server, usuario, loja, entrar):
    entrar(usuario)
    page.goto(live_server.url + f"/loja/{loja.id_loja}/")

    page.fill("#comentario-loja", "Comentário sem nota")
    page.get_by_role("button", name="ENVIAR COMENTÁRIO").click()

    assert Avaliacao.objects.count() == 0
    assert page.evaluate("document.querySelector('#estrela5').validity.valueMissing") is True


# ------------------------------- CT-001 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("origem", ["/suporte/", "/tutorial/", "/perfil-loja/"])
def test_ct001_botao_inicio_leva_para_a_pagina_inicial(ir, page, live_server, usuario, entrar, origem):
    entrar(usuario)                                  # com login, as três telas abrem normalmente
    ir(origem)

    page.locator(".topbar").get_by_role("link", name="Início", exact=True).click()   # botão da barra superior

    expect(page).to_have_url(live_server.url + "/")
    expect(page.locator('input[name="q"]')).to_be_visible()        # campo de pesquisa da home
    expect(page.get_by_text("Pesquise alguma loja ou produto que deseje...")).to_be_visible()


# ------------------------------- CT-002 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct002_botao_minha_conta_leva_o_usuario_autenticado_ao_seu_perfil(ir, page, live_server, usuario, entrar):
    entrar(usuario)
    ir("/")

    botao = page.get_by_role("button", name=re.compile("Minha conta"))
    expect(botao).to_be_visible()
    botao.click()

    expect(page).to_have_url(live_server.url + "/perfil-consumidor/")
    expect(page.locator('input[name="nome"]')).to_have_value("Maria")


# ------------------------------- CT-003 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct003_botao_do_topo_leva_o_visitante_ao_cadastro(ir, page, live_server):
    ir("/")

    page.get_by_role("button", name="Criar conta ou Entrar").click()

    expect(page).to_have_url(live_server.url + "/cadastro/")
    expect(page.locator('input[name="nome"]')).to_be_visible()
    expect(page.locator('input[name="senha"]')).to_be_visible()


# ------------------------------- CT-014 / CT-015 ---------------------------- #
@pytest.mark.django_db(transaction=True)
def test_ct014_botao_produtos_abre_o_gerenciamento_de_produtos(ir, page, live_server, usuario, loja, entrar):
    entrar(usuario)
    ir("/perfil-loja/")

    page.get_by_role("button", name="PRODUTOS").click()

    expect(page).to_have_url(live_server.url + "/produtos-loja/")


@pytest.mark.django_db(transaction=True)
def test_ct015_botao_servicos_abre_o_gerenciamento_de_servicos(ir, page, live_server, usuario, loja, entrar):
    entrar(usuario)
    ir("/perfil-loja/")

    page.get_by_role("button", name="SERVIÇOS").click()

    expect(page).to_have_url(live_server.url + "/servicos-loja/")


# ------------------------------- CT-050 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct050_botao_adicionar_loja_favorita_leva_a_tela_inicial_com_a_busca(ir, page, live_server, usuario, entrar):
    entrar(usuario)                              # já cai no perfil do consumidor, sem favoritas

    page.get_by_role("button", name="Procurar lojas").click()

    expect(page).to_have_url(live_server.url + "/")
    expect(page.locator('input[name="q"]')).to_be_visible()


# --------------------- Login e logout pela interface ------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct052_ct053_login_e_logout_pela_interface(ir, page, live_server, usuario, entrar):
    entrar(usuario)                              # CT-053: login válido → perfil
    expect(page).to_have_url(live_server.url + "/perfil-consumidor/")

    page.get_by_role("button", name=re.compile("Fazer Logout")).click()   # CT-052

    expect(page).to_have_url(live_server.url + "/")
    expect(page.get_by_role("button", name="Criar conta ou Entrar")).to_be_visible()

    ir("/perfil-consumidor/")                    # área restrita sem login → tela de login
    expect(page).to_have_url(re.compile(r"/login/$"))


@pytest.mark.django_db(transaction=True)
def test_ct054_login_com_senha_errada_mostra_mensagem_e_nao_entra(ir, page, live_server, usuario):
    ir("/login/")
    page.fill('input[name="email"]', usuario.email)
    page.fill('input[name="senha"]', "SenhaErrada1")
    page.click("button.login-submit-btn")

    expect(page.locator(".alert")).to_contain_text("E-mail ou senha inválidos")
    expect(page).to_have_url(re.compile(r"/login/$"))