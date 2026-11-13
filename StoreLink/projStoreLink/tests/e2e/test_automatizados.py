import re
import pytest
from playwright.sync_api import expect
from AppStoreLink.models import Avaliacao, Loja
from tests.conftest import RespostaFalsa

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
def test_ct038_ct041_usuario_avalia_a_loja_e_o_comentario_permanece_apos_atualizar(page, live_server, usuario, loja, entrar):
    entrar(usuario)
    page.goto(live_server.url + f"/loja/{loja.id_loja}/")

    page.locator('label[for="estrela5"]').click()                               # 5 estrelas
    page.fill("#comentario-loja", "Ótimo atendimento e produtos de qualidade.")
    page.get_by_role("button", name="ENVIAR COMENTÁRIO").click()

    texto = page.locator("article.info-comentario-card p", has_text="Ótimo atendimento e produtos de qualidade.")
    expect(texto).to_be_visible()                                               # aparece na lista
    avaliacao = Avaliacao.objects.get()
    assert (avaliacao.nota, avaliacao.id_usuario, avaliacao.id_loja) == (5, usuario, loja)

    page.reload()                                                               # CT-041: atualizar a página
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
def test_ct001_botao_inicio_leva_para_a_pagina_inicial(ir, page, live_server, origem):
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


# ------------------------------- CT-051 ------------------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct051_botao_adicionar_loja_favorita_leva_a_tela_inicial_com_a_busca(ir, page, live_server, usuario, entrar):
    entrar(usuario)                              # já cai no perfil do consumidor, sem favoritas

    page.get_by_role("button", name="Procurar lojas").click()

    expect(page).to_have_url(live_server.url + "/")
    expect(page.locator('input[name="q"]')).to_be_visible()


# --------------------- Login e logout pela interface ------------------------ #
@pytest.mark.django_db(transaction=True)
def test_ct053_ct054_login_e_logout_pela_interface(ir, page, live_server, usuario, entrar):
    entrar(usuario)                              # CT-054: login válido → perfil
    expect(page).to_have_url(live_server.url + "/perfil-consumidor/")

    page.get_by_role("button", name=re.compile("Fazer Logout")).click()   # CT-053

    expect(page).to_have_url(live_server.url + "/")
    expect(page.get_by_role("button", name="Criar conta ou Entrar")).to_be_visible()

    ir("/perfil-consumidor/")                    # área restrita sem login → tela de login
    expect(page).to_have_url(re.compile(r"/login/$"))


@pytest.mark.django_db(transaction=True)
def test_ct055_login_com_senha_errada_mostra_mensagem_e_nao_entra(ir, page, live_server, usuario):
    ir("/login/")
    page.fill('input[name="email"]', usuario.email)
    page.fill('input[name="senha"]', "SenhaErrada1")
    page.click("button.login-submit-btn")

    expect(page.locator(".alert")).to_contain_text("E-mail ou senha inválidos")
    expect(page).to_have_url(re.compile(r"/login/$"))