"""
Ajudantes dos testes de INTEGRAÇÃO feitos pela interface (navegador real - Playwright).

Como funciona:
  • `live_server` (pytest-django) sobe o seu site de verdade numa porta livre, com um banco de
    teste vazio e descartável.
  • `page` (pytest-playwright) é uma aba de um Chromium real, controlada pelo teste.
  Usar `live_server` num teste já faz o banco ser compartilhado com o servidor (transacional).
"""
import pytest

from tests.conftest import SENHA_VALIDA


@pytest.fixture
def browser_context_args(browser_context_args):
    """Idioma do navegador igual ao do site."""
    return {**browser_context_args, "locale": "pt-BR"}


@pytest.fixture
def ir(page, live_server):
    """ir('/suporte/') abre uma página do site no navegador."""
    def _ir(caminho="/"):
        page.goto(live_server.url + caminho)
        return page
    return _ir


@pytest.fixture
def entrar(page, live_server):
    """entrar(usuario) faz o login DE VERDADE pela tela (digita e-mail e senha e clica em ENTRAR)."""
    def _entrar(usuario, senha=SENHA_VALIDA):
        page.goto(live_server.url + "/login/")
        page.fill('input[name="email"]', usuario.email)
        page.fill('input[name="senha"]', senha)
        page.click("button.login-submit-btn")
        page.wait_for_url("**/perfil-consumidor/")
    return _entrar