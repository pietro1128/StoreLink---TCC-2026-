//#region TEMA
// Cuida do modo claro/escuro em todas as páginas.
function atualizarBotaoTema(botao = document.querySelector('.theme-toggle')) {
  if (!botao) return;
  const escuro = document.body.classList.contains('dark');
  botao.innerHTML = escuro
    ? '<span class="sl-icon sl-sun" aria-hidden="true"></span><span class="theme-label">Modo claro</span>'
    : '<span class="sl-icon sl-moon" aria-hidden="true"></span><span class="theme-label">Modo escuro</span>';
}

function toggleTheme(botao) {
  document.body.classList.toggle('dark');
  localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
  atualizarBotaoTema(botao);
}

function iniciarTema() {
  if (localStorage.getItem('theme') === 'dark') document.body.classList.add('dark');
  atualizarBotaoTema();
}
//#endregion

//#region NAVEGAÇÃO
// Centraliza os botões que navegam usando data-url.
function setActiveNav(botao) {
  if (!botao) return;
  document.querySelectorAll('.nav-btn').forEach(item => item.classList.remove('active'));
  botao.classList.add('active');
}

function navegar(elemento) {
  if (elemento?.dataset.url) window.location.href = elemento.dataset.url;
}
//#endregion

//#region IMAGENS
// Faz o preview das imagens selecionadas sem repetir o mesmo código em cada tela.
function prepararPreviewImagem(input, preview, area) {
  if (!input || !preview || !area || input.dataset.previewPreparado) return;
  input.dataset.previewPreparado = '1';

  if (preview.getAttribute('src')) area.classList.add('tem-imagem');

  area.querySelectorAll('[class*="botao-imagem"], [class*="trocar-imagem"]').forEach(botao => {
    botao.addEventListener('click', () => input.click());
  });

  input.addEventListener('change', function () {
    const arquivo = this.files?.[0];
    if (!arquivo) return;

    if (!arquivo.type.startsWith('image/')) {
      alert('Selecione um arquivo de imagem.');
      this.value = '';
      return;
    }

    const url = URL.createObjectURL(arquivo);
    preview.src = url;
    area.classList.add('tem-imagem');
    preview.onload = () => URL.revokeObjectURL(url);
  });
}

function iniciarImagens() {
  document.querySelectorAll('.produto-imagem').forEach(area => {
    prepararPreviewImagem(area.querySelector('.produto-imagem-input'), area.querySelector('.produto-preview'), area);
  });

  document.querySelectorAll('.servico-imagem').forEach(area => {
    prepararPreviewImagem(area.querySelector('.servico-imagem-input'), area.querySelector('.servico-preview'), area);
  });

  prepararPreviewImagem(
    document.getElementById('foto-consumidor'),
    document.getElementById('preview-consumidor'),
    document.querySelector('.consumidor-avatar')
  );

  prepararPreviewImagem(
    document.getElementById('foto-estabelecimento'),
    document.getElementById('preview-estabelecimento'),
    document.querySelector('.perfil-cover')
  );
}

// Substitui os antigos onerror dos HTMLs.
function tratarErroImagem(imagem) {
  imagem.classList.add('imagem-falhou');
  const fallback = imagem.nextElementSibling;
  if (fallback?.matches('.info-sem-imagem, .tutorial-sem-print')) {
    fallback.classList.add('imagem-fallback-visivel');
  }
}
//#endregion

//#region PERFIL DO CONSUMIDOR
// Libera nome e sobrenome só quando o usuário clica em editar.
function editarConsumidor(botao) {
  const form = document.getElementById('formEditarConsumidor');
  if (!form) return;

  const editando = !form.classList.contains('editando');
  form.classList.toggle('editando', editando);
  form.querySelectorAll('input[name="nome"], input[name="sobrenome"]').forEach(campo => campo.readOnly = !editando);

  const salvar = form.querySelector('.consumidor-salvar-alteracoes');
  if (salvar) salvar.hidden = !editando;

  if (editando) {
    botao.innerHTML = '<span class="sl-icon sl-x" aria-hidden="true"></span> Cancelar edição';
    form.querySelector('input[name="nome"]')?.focus();
  } else {
    botao.innerHTML = '<span class="sl-icon sl-pencil" aria-hidden="true"></span> Editar usuário';
    form.reset();
  }
}
//#endregion

//#region PERFIL DA LOJA
// Monta o dropdown de classificação usando as mesmas cores da sidebar.
const classesCategorias = {
  'Alimentos': 'cat-alimentos',
  'Moda': 'cat-moda',
  'Esportes': 'cat-esportes',
  'Construção': 'cat-construcao',
  'Saúde': 'cat-saude',
  'Pets': 'cat-pets',
  'Ambiente': 'cat-ambiente',
  'Tecnologia': 'cat-tecnologia',
  'Beleza': 'cat-beleza',
  'Outros': 'cat-outros'
};

const classesClassificacao = {
  'Alimentos': 'classificacao-alimentos',
  'Moda': 'classificacao-moda',
  'Esportes': 'classificacao-esportes',
  'Construção': 'classificacao-construcao',
  'Saúde': 'classificacao-saude',
  'Pets': 'classificacao-pets',
  'Ambiente': 'classificacao-ambiente',
  'Tecnologia': 'classificacao-tecnologia',
  'Beleza': 'classificacao-beleza',
  'Outros': 'classificacao-outros'
};

function aplicarClassificacao(nome, valor = nome) {
  const texto = document.getElementById('classifName');
  const input = document.getElementById('categoria-input');
  if (!texto || !input) return;

  texto.textContent = nome;
  input.value = valor;

  Object.values(classesClassificacao).forEach(classe => document.body.classList.remove(classe));
  document.body.classList.add(classesClassificacao[valor] || classesClassificacao.Outros);
}

function iniciarClassificacaoLoja() {
  const botao = document.getElementById('classifBtn');
  const dropdown = document.getElementById('classifDropdown');
  const input = document.getElementById('categoria-input');
  if (!botao || !dropdown || !input || dropdown.dataset.preparado) return;
  dropdown.dataset.preparado = '1';

  Object.keys(classesCategorias).forEach(nome => {
    const opcao = document.createElement('button');
    opcao.type = 'button';
    opcao.className = `perfil-classif-option ${classesCategorias[nome]}`;
    opcao.textContent = nome;
    opcao.addEventListener('click', evento => {
      evento.stopPropagation();

      if (nome === 'Outros') {
        const personalizado = prompt('Digite o nome da classificação da loja:');
        if (personalizado?.trim()) aplicarClassificacao(personalizado.trim(), nome);
      } else {
        aplicarClassificacao(nome, nome);
      }

      dropdown.classList.remove('open');
    });
    dropdown.appendChild(opcao);
  });

  aplicarClassificacao(input.value.trim() || 'Alimentos', input.value.trim() || 'Alimentos');

  botao.addEventListener('click', evento => {
    evento.stopPropagation();
    dropdown.classList.toggle('open');
  });

  document.addEventListener('click', () => dropdown.classList.remove('open'));
}

// Consulta o CEP e preenche a rua, igual ao código que antes ficava no HTML.
function iniciarCep() {
  const campoCep = document.querySelector('[name="cep"]');
  if (!campoCep || campoCep.dataset.cepPreparado) return;
  campoCep.dataset.cepPreparado = '1';

  campoCep.addEventListener('blur', async () => {
    const cep = campoCep.value.replace(/\D/g, '');
    if (cep.length !== 8) return;

    try {
      const resposta = await fetch(`/api/cep/${cep}/`);
      const dados = await resposta.json();

      if (!resposta.ok) {
        alert(dados.erro);
        return;
      }

      const rua = document.querySelector('[name="rua"]');
      if (rua && dados.rua) rua.value = dados.rua;

      const proximo = document.querySelector(dados.rua ? '[name="numero"]' : '[name="rua"]');
      proximo?.focus();
    } catch (_) {
      alert('Não foi possível consultar o CEP agora.');
    }
  });
}
//#endregion

//#region PRODUTOS
// A cor do card já vem do CSS da categoria da loja; aqui só cuidamos dos estados do formulário.
function atualizarCategoriaProduto(select) {
  const card = select?.closest('.produto-card-novo');
  if (!card) return;

  const categoria = select.options[select.selectedIndex]?.dataset.categoria || '';
  const texto = card.querySelector('.produto-categoria-selecionada');
  card.classList.toggle('tem-categoria', !!categoria);
  if (texto) texto.textContent = categoria || 'Nenhuma categoria selecionada';
}

function adicionarProduto() {
  const novo = document.getElementById('produtoCardNovo');
  const criar = document.getElementById('produtoCriarCard');
  if (!novo || !criar) return;

  novo.classList.add('aberto');
  criar.classList.add('oculto');
  novo.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  novo.querySelector('input[name="nome_produto"]')?.focus();
}

function cancelarNovoProduto() {
  const novo = document.getElementById('produtoCardNovo');
  const criar = document.getElementById('produtoCriarCard');
  const form = document.getElementById('formNovoProduto');
  if (!novo || !criar || !form) return;

  form.reset();
  const imagem = novo.querySelector('.produto-imagem');
  const preview = imagem?.querySelector('.produto-preview');
  imagem?.classList.remove('tem-imagem');
  preview?.removeAttribute('src');
  novo.classList.remove('tem-categoria', 'aberto');

  const categoria = novo.querySelector('.produto-categoria-selecionada');
  if (categoria) categoria.textContent = 'Nenhuma categoria selecionada';
  criar.classList.remove('oculto');
}

function editarProduto(botao) {
  const card = botao?.closest('.produto-card-salvo');
  if (!card) return;

  const editando = !card.classList.contains('editando');
  card.classList.toggle('editando', editando);
  card.querySelectorAll('.produto-form-salvo input, .produto-form-salvo textarea').forEach(campo => campo.readOnly = !editando);

  const salvar = card.querySelector('.produto-salvar-alteracoes');
  if (salvar) salvar.hidden = !editando;
  if (editando) card.querySelector('input[name="nome_produto"]')?.focus();
}
//#endregion

//#region SERVIÇOS
// Mesma lógica dos produtos, mas aplicada aos cards de serviço.
function atualizarCategoriaServico(select) {
  const card = select?.closest('.servico-card-novo');
  if (!card) return;

  const categoria = select.options[select.selectedIndex]?.dataset.categoria || '';
  const texto = card.querySelector('.servico-categoria-selecionada');
  card.classList.toggle('tem-categoria', !!categoria);
  if (texto) texto.textContent = categoria || 'Nenhuma categoria selecionada';
}

function adicionarServico() {
  const novo = document.getElementById('servicoCardNovo');
  const criar = document.getElementById('servicoCriarCard');
  if (!novo || !criar) return;

  novo.classList.add('aberto');
  criar.classList.add('oculto');
  novo.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  novo.querySelector('input[name="nome_servico"]')?.focus();
}

function cancelarNovoServico() {
  const novo = document.getElementById('servicoCardNovo');
  const criar = document.getElementById('servicoCriarCard');
  const form = document.getElementById('formNovoServico');
  if (!novo || !criar || !form) return;

  form.reset();
  const imagem = novo.querySelector('.servico-imagem');
  const preview = imagem?.querySelector('.servico-preview');
  imagem?.classList.remove('tem-imagem');
  preview?.removeAttribute('src');
  novo.classList.remove('tem-categoria', 'aberto');

  const categoria = novo.querySelector('.servico-categoria-selecionada');
  if (categoria) categoria.textContent = 'Nenhuma categoria selecionada';
  criar.classList.remove('oculto');
}

function editarServico(botao) {
  const card = botao?.closest('.servico-card-salvo');
  if (!card) return;

  const editando = !card.classList.contains('editando');
  card.classList.toggle('editando', editando);
  card.querySelectorAll('.servico-form-salvo input, .servico-form-salvo textarea').forEach(campo => campo.readOnly = !editando);

  const salvar = card.querySelector('.servico-salvar-alteracoes');
  if (salvar) salvar.hidden = !editando;
  if (editando) card.querySelector('input[name="nome_servico"]')?.focus();
}
//#endregion

//#region INFORMAÇÕES DA LOJA
// Abre e fecha a edição dos comentários e dos dados da loja.
function abrirEdicao(botao) {
  botao?.closest('.info-comentario-card')?.classList.add('editando');
}

function fecharEdicao(botao) {
  botao?.closest('.info-comentario-card')?.classList.remove('editando');
}

function abrirEdicaoLoja(botao) {
  const card = botao?.closest('.info-loja-card');
  if (!card) return;

  const valor = (seletor, fallback = '') => card.querySelector(seletor)?.textContent.trim() ?? fallback;
  const preencher = (seletor, dado) => {
    const campo = card.querySelector(seletor);
    if (campo) campo.value = dado;
  };

  preencher('.js-editar-loja-nome', valor('.js-loja-nome'));
  preencher('.js-editar-loja-rua', valor('.js-loja-rua'));
  preencher('.js-editar-loja-numero', valor('.js-loja-numero'));
  preencher('.js-editar-loja-cep', valor('.js-loja-cep'));
  preencher('.js-editar-loja-email', valor('.js-loja-email'));

  const telefone = valor('.js-loja-telefone');
  preencher('.js-editar-loja-telefone', telefone === 'Não informado' ? '' : telefone);
  preencher('.js-editar-loja-cnpj', valor('.js-loja-cnpj'));

  const linkElemento = card.querySelector('.js-loja-link');
  const link = linkElemento ? (linkElemento.dataset.link || linkElemento.textContent.trim()) : '';
  preencher('.js-editar-loja-link', link === 'Não possui' ? '' : link);
  preencher('.js-editar-loja-categoria', valor('.js-loja-categoria'));
  card.classList.add('editando');
}

function cancelarEdicaoLoja(botao) {
  botao?.closest('.info-loja-card')?.classList.remove('editando');
}
//#endregion

//#region INFORMAÇÕES DE PRODUTO E SERVIÇO
// Preenche o formulário de edição com o que já está aparecendo no card.
function abrirEdicaoItem(botao, tipo) {
  const card = botao?.closest(`.info-${tipo}-card`);
  if (!card) return;

  const nome = card.querySelector('.js-nome');
  const preco = card.querySelector('.js-preco');
  const descricao = card.querySelector('.js-descricao');
  const inputNome = card.querySelector('.js-editar-nome');
  const inputPreco = card.querySelector('.js-editar-preco');
  const inputDescricao = card.querySelector('.js-editar-descricao');
  if (!nome || !preco || !descricao || !inputNome || !inputPreco || !inputDescricao) return;

  inputNome.value = nome.textContent.trim();
  inputPreco.value = preco.textContent.replace('R$', '').trim();
  const atual = descricao.textContent.trim();
  inputDescricao.value = atual === 'Sem descrição.' ? '' : atual;
  card.classList.add('editando');
}

function abrirEdicaoProduto(botao) { abrirEdicaoItem(botao, 'produto'); }
function abrirEdicaoServico(botao) { abrirEdicaoItem(botao, 'servico'); }
function cancelarEdicaoProduto(botao) { botao?.closest('.info-produto-card')?.classList.remove('editando'); }
function cancelarEdicaoServico(botao) { botao?.closest('.info-servico-card')?.classList.remove('editando'); }
//#endregion

//#region FAVORITOS
// Busca os favoritos do usuário e deixa cada coração no estado certo.
function pegarIdLojaFavorito(form) {
  const resultado = form?.getAttribute('action')?.match(/\/loja\/(\d+)\/favoritar\/?/);
  return resultado?.[1] || null;
}

function atualizarCoracoesFavoritos(lojasFavoritas) {
  document.querySelectorAll('form[action*="/favoritar/"]').forEach(form => {
    const idLoja = pegarIdLojaFavorito(form);
    const botao = form.querySelector('.loja-card-fav, .resultado-card-fav, .info-favoritar');
    if (!idLoja || !botao) return;

    const ativo = lojasFavoritas.includes(idLoja);
    botao.innerHTML = ativo
      ? '<span class="sl-icon sl-heart-fill" aria-hidden="true"></span>'
      : '<span class="sl-icon sl-heart" aria-hidden="true"></span>';
    botao.setAttribute('aria-label', ativo ? 'Remover dos favoritos' : 'Favoritar loja');
    botao.setAttribute('title', ativo ? 'Remover dos favoritos' : 'Favoritar loja');
  });
}

async function carregarFavoritos() {
  if (!document.querySelector('form[action*="/favoritar/"]')) return;

  try {
    const resposta = await fetch('/perfil-consumidor/', { method: 'GET', credentials: 'same-origin', cache: 'no-store' });
    if (!resposta.ok) return;

    const documento = new DOMParser().parseFromString(await resposta.text(), 'text/html');
    const favoritos = [];
    documento.querySelectorAll('form[action*="/favoritar/"]').forEach(form => {
      const id = pegarIdLojaFavorito(form);
      if (id && !favoritos.includes(id)) favoritos.push(id);
    });
    atualizarCoracoesFavoritos(favoritos);
  } catch (_) {
    // Se não der para consultar, o coração fica no estado que veio do HTML.
  }
}
//#endregion

//#region EVENTOS
// Um único lugar cuida dos cliques que antes estavam espalhados como onclick nos HTMLs.
function iniciarEventos() {
  document.addEventListener('click', evento => {
    const alvo = evento.target;
    if (!(alvo instanceof Element)) return;

    const tema = alvo.closest('.theme-toggle');
    if (tema) {
      toggleTheme(tema);
      return;
    }

    const editarConsumidorBtn = alvo.closest('.consumidor-editar-btn');
    if (editarConsumidorBtn) {
      editarConsumidor(editarConsumidorBtn);
      return;
    }

    const cancelarLoja = alvo.closest('.info-loja-cancelar');
    if (cancelarLoja) {
      cancelarEdicaoLoja(cancelarLoja);
      return;
    }

    const editarComentario = alvo.closest('.info-comentario-editar');
    if (editarComentario) {
      abrirEdicao(editarComentario);
      return;
    }

    const editarItem = alvo.closest('.info-item-editar');
    if (editarItem) {
      if (editarItem.closest('.info-produto-card')) abrirEdicaoProduto(editarItem);
      else if (editarItem.closest('.info-servico-card')) abrirEdicaoServico(editarItem);
      return;
    }

    const cancelarEdicao = alvo.closest('.info-edicao-cancelar');
    if (cancelarEdicao) {
      if (cancelarEdicao.closest('.info-produto-card')) cancelarEdicaoProduto(cancelarEdicao);
      else if (cancelarEdicao.closest('.info-servico-card')) cancelarEdicaoServico(cancelarEdicao);
      else if (cancelarEdicao.closest('.info-comentario-card')) fecharEdicao(cancelarEdicao);
      return;
    }

    const editarProdutoBtn = alvo.closest('.produto-editar-info');
    if (editarProdutoBtn) {
      editarProduto(editarProdutoBtn);
      return;
    }

    if (alvo.closest('.produto-cancelar-card')) {
      cancelarNovoProduto();
      return;
    }

    if (alvo.closest('.produto-criar-card-btn')) {
      adicionarProduto();
      return;
    }

    const editarServicoBtn = alvo.closest('.servico-editar-info');
    if (editarServicoBtn) {
      editarServico(editarServicoBtn);
      return;
    }

    if (alvo.closest('.servico-cancelar-card')) {
      cancelarNovoServico();
      return;
    }

    if (alvo.closest('.servico-criar-card-btn')) {
      adicionarServico();
      return;
    }

    const confirmarClique = alvo.closest('[data-confirm-click]');
    if (confirmarClique && !confirm(confirmarClique.dataset.confirmClick)) {
      evento.preventDefault();
      return;
    }

    // Favoritar não pode acionar a navegação do card que está por trás.
    if (alvo.closest('form[action*="/favoritar/"]')) return;

    const navegavel = alvo.closest('[data-url]');
    if (navegavel) navegar(navegavel);
  });

  document.addEventListener('change', evento => {
    const alvo = evento.target;
    if (!(alvo instanceof Element)) return;
    if (alvo.matches('.produto-categoria-select')) atualizarCategoriaProduto(alvo);
    if (alvo.matches('.servico-categoria-select')) atualizarCategoriaServico(alvo);
  });

  document.addEventListener('submit', evento => {
    const form = evento.target;
    if (!(form instanceof HTMLFormElement) || !form.dataset.confirm) return;
    if (!confirm(form.dataset.confirm)) evento.preventDefault();
  });

  document.addEventListener('error', evento => {
    if (evento.target instanceof HTMLImageElement) tratarErroImagem(evento.target);
  }, true);
}
//#endregion

//#region INICIALIZAÇÃO
// Liga só o que existe na página atual.
function iniciarPagina() {
  iniciarTema();
  iniciarEventos();
  iniciarImagens();
  iniciarClassificacaoLoja();
  iniciarCep();
  carregarFavoritos();
}

document.addEventListener('DOMContentLoaded', iniciarPagina);
//#endregion

document.addEventListener('DOMContentLoaded', function () {
  // ---- Editar loja ----
  var btnEditar = document.querySelector('.info-editar-loja');
  var btnCancelar = document.querySelector('.info-loja-cancelar');
  var visualizacao = document.querySelector('.info-loja-visualizacao');
  var edicao = document.querySelector('.info-loja-edicao');

  if (btnEditar && btnCancelar && visualizacao && edicao) {
    edicao.style.display = 'none'; // começa escondido

    btnEditar.addEventListener('click', function () {
      visualizacao.style.display = 'none';
      edicao.style.display = 'block';
    });

    btnCancelar.addEventListener('click', function () {
      edicao.style.display = 'none';
      visualizacao.style.display = '';
    });
  }

  // ---- Excluir loja (pede confirmação) ----
  var formExcluir = document.querySelector('.info-excluir-form');

  if (formExcluir) {
    formExcluir.addEventListener('submit', function (e) {
      if (!confirm('Deseja excluir esta loja?')) {
        e.preventDefault();
      }
    });
  }
});


document.querySelectorAll('.info-comentario-card').forEach(function (card) {
  var edicao = card.querySelector('.info-comentario-edicao');
  if (!edicao) return; // comentário de outra pessoa, não tem botões

  var texto = card.querySelector(':scope > p');
  var acoes = card.querySelector('.info-comentario-acoes');
  var btnEditar = card.querySelector('.info-comentario-editar');
  var btnCancelar = card.querySelector('.info-edicao-cancelar');

  edicao.style.display = 'none'; // começa escondido

  btnEditar.addEventListener('click', function () {
    texto.style.display = 'none';
    acoes.style.display = 'none';
    edicao.style.display = 'block';
  });

  btnCancelar.addEventListener('click', function () {
    edicao.style.display = 'none';
    texto.style.display = '';
    acoes.style.display = '';
  });
});


document.querySelectorAll('.info-servico-card').forEach(function (card) {
    var editar = card.querySelector('.info-item-editar');
    var cancelar = card.querySelector('.info-edicao-cancelar');
    var visualizacao = card.querySelector('.info-item-visualizacao');
    var edicao = card.querySelector('.info-item-edicao');

    if (!editar || !edicao) return;

    editar.addEventListener('click', function () {
      visualizacao.style.display = 'none';   // esconde os textos
      edicao.style.display = 'block';        // mostra os campos para editar
    });

    cancelar.addEventListener('click', function () {
      edicao.reset();                        // desfaz o que foi digitado
      edicao.style.display = '';             // volta ao padrão do CSS
      visualizacao.style.display = '';
    });
  });