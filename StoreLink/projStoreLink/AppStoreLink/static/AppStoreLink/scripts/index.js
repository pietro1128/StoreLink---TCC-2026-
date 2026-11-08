//#region NAVBAR

function setActiveNav(btn) {

    if (!btn || !btn.classList) {
        return;
    }

    document
        .querySelectorAll('.nav-btn')
        .forEach(function (botao) {

            botao.classList.remove('active');

        });

    btn.classList.add('active');
}

//#endregion



//#region MODO ESCURO

function toggleTheme(btn) {

    document.body.classList.toggle('dark');

    const modoEscuro =
        document.body.classList.contains('dark');

    localStorage.setItem(
        'theme',
        modoEscuro ? 'dark' : 'light'
    );

    if (btn) {

        btn.innerHTML =
            modoEscuro
                ? '<i class="bi bi-sun-fill" aria-hidden="true"></i> <span class="theme-label">Modo claro</span>'
                : '<i class="bi bi-moon-fill" aria-hidden="true"></i> <span class="theme-label">Modo escuro</span>';

    }
}

//#endregion



//#region PRODUTOS

function prepararProdutoCard(card) {

    if (!card) {
        return;
    }


    const areaImagem =
        card.querySelector('.produto-imagem');


    if (!areaImagem) {
        return;
    }


    const input =
        areaImagem.querySelector(
            '.produto-imagem-input'
        );


    const preview =
        areaImagem.querySelector(
            '.produto-preview'
        );


    const botaoAdicionar =
        areaImagem.querySelector(
            '.produto-botao-imagem'
        );


    const botaoTrocar =
        areaImagem.querySelector(
            '.produto-trocar-imagem'
        );


    if (!input || !preview) {
        return;
    }


    if (
        preview.classList.contains(
            'produto-preview-existente'
        )
        ||
        preview.getAttribute('src')
    ) {

        areaImagem.classList.add(
            'tem-imagem'
        );

    }


    if (botaoAdicionar) {

        botaoAdicionar.onclick =
            function () {

                input.click();

            };

    }


    if (botaoTrocar) {

        botaoTrocar.onclick =
            function () {

                input.click();

            };

    }


    input.onchange =
        function () {

            const arquivo =
                input.files[0];


            if (!arquivo) {
                return;
            }


            if (
                !arquivo.type.startsWith('image/')
            ) {

                alert(
                    'Selecione um arquivo de imagem.'
                );

                input.value = '';

                return;
            }


            const urlImagem =
                URL.createObjectURL(
                    arquivo
                );


            preview.src =
                urlImagem;


            areaImagem.classList.add(
                'tem-imagem'
            );


            preview.onload =
                function () {

                    URL.revokeObjectURL(
                        urlImagem
                    );

                };

        };

}



function criarProdutoCard() {

    const card =
        document.createElement('div');


    card.className =
        'produto-card';


    card.innerHTML = `

        <button
            type="button"
            class="produto-excluir-card"
            onclick="excluirProdutoCard(this)"
            title="Excluir produto"
            aria-label="Excluir produto"
        >
            <i class="bi bi-trash3" aria-hidden="true"></i>
        </button>


        <div class="produto-imagem">

            <input
                class="produto-imagem-input"
                type="file"
                accept="image/*"
                hidden
            >


            <button
                type="button"
                class="produto-botao-imagem"
            >
                <i class="bi bi-camera-plus" aria-hidden="true"></i>
                Adicionar imagem
            </button>


            <img
                class="produto-preview"
                alt="Imagem do produto"
            >


            <button
                type="button"
                class="produto-trocar-imagem"
                title="Trocar imagem"
                aria-label="Trocar imagem"
            >
                <i class="bi bi-pencil" aria-hidden="true"></i>
            </button>

        </div>


        <div class="produto-form">

            <label>
                Nome do produto
            </label>

            <input
                type="text"
                name="nome_produto"
                placeholder="Nome do produto"
            >


            <label>
                Preço
            </label>

            <input
                type="text"
                name="preco_produto"
                placeholder="0,00"
            >


            <label>
                Descrição
            </label>

            <textarea
                name="descricao_produto"
                placeholder="Descrição do produto"
            ></textarea>

        </div>

    `;


    prepararProdutoCard(card);


    return card;

}



function adicionarProduto() {

    const container =
        document.querySelector(
            '.produto-cards-scroll'
        );


    if (!container) {
        return;
    }


    const novoCard =
        criarProdutoCard();


    const cardAdicionar =
        document.getElementById(
            'produtoCriarCard'
        );


    if (cardAdicionar) {

        container.insertBefore(
            novoCard,
            cardAdicionar
        );

    } else {

        container.appendChild(
            novoCard
        );

    }

}



function excluirProdutoCard(botao) {

    const card =
        botao.closest(
            '.produto-card'
        );


    if (!card) {
        return;
    }


    const confirmar =
        confirm(
            'Deseja excluir este produto?'
        );


    if (!confirmar) {
        return;
    }


    card.remove();

}

//#endregion



//#region SERVIÇOS

function prepararServicoCard(card) {

    if (!card) {
        return;
    }


    const areaImagem =
        card.querySelector(
            '.servico-imagem'
        );


    if (!areaImagem) {
        return;
    }


    const input =
        areaImagem.querySelector(
            '.servico-imagem-input'
        );


    const preview =
        areaImagem.querySelector(
            '.servico-preview'
        );


    const botaoAdicionar =
        areaImagem.querySelector(
            '.servico-botao-imagem'
        );


    const botaoTrocar =
        areaImagem.querySelector(
            '.servico-trocar-imagem'
        );


    if (!input || !preview) {
        return;
    }


    if (
        preview.classList.contains(
            'servico-preview-existente'
        )
        ||
        preview.getAttribute('src')
    ) {

        areaImagem.classList.add(
            'tem-imagem'
        );

    }


    if (botaoAdicionar) {

        botaoAdicionar.onclick =
            function () {

                input.click();

            };

    }


    if (botaoTrocar) {

        botaoTrocar.onclick =
            function () {

                input.click();

            };

    }


    input.onchange =
        function () {

            const arquivo =
                input.files[0];


            if (!arquivo) {
                return;
            }


            if (
                !arquivo.type.startsWith('image/')
            ) {

                alert(
                    'Selecione um arquivo de imagem.'
                );

                input.value = '';

                return;
            }


            const urlImagem =
                URL.createObjectURL(
                    arquivo
                );


            preview.src =
                urlImagem;


            areaImagem.classList.add(
                'tem-imagem'
            );


            preview.onload =
                function () {

                    URL.revokeObjectURL(
                        urlImagem
                    );

                };

        };

}



function criarServicoCard() {

    const card =
        document.createElement('div');


    card.className =
        'servico-card';


    card.innerHTML = `

        <button
            type="button"
            class="servico-excluir-card"
            onclick="excluirServicoCard(this)"
            title="Excluir serviço"
            aria-label="Excluir serviço"
        >
            <i class="bi bi-trash3" aria-hidden="true"></i>
        </button>


        <div class="servico-imagem">

            <input
                class="servico-imagem-input"
                type="file"
                accept="image/*"
                hidden
            >


            <button
                type="button"
                class="servico-botao-imagem"
            >
                <i class="bi bi-camera-plus" aria-hidden="true"></i>
                Adicionar imagem
            </button>


            <img
                class="servico-preview"
                alt="Imagem do serviço"
            >


            <button
                type="button"
                class="servico-trocar-imagem"
                title="Trocar imagem"
                aria-label="Trocar imagem"
            >
                <i class="bi bi-pencil" aria-hidden="true"></i>
            </button>

        </div>


        <div class="servico-form">

            <label>
                Nome do serviço
            </label>

            <input
                type="text"
                name="nome_servico"
                placeholder="Nome do serviço"
            >


            <label>
                Preço
            </label>

            <input
                type="text"
                name="preco"
                placeholder="0,00"
            >


            <label>
                Descrição
            </label>

            <textarea
                name="descricao"
                placeholder="Descrição do serviço"
            ></textarea>

        </div>

    `;


    prepararServicoCard(card);


    return card;

}



function adicionarServico() {

    const container =
        document.querySelector(
            '.servico-cards-scroll'
        );


    if (!container) {
        return;
    }


    const novoCard =
        criarServicoCard();


    const cardAdicionar =
        document.getElementById(
            'servicoCriarCard'
        );


    if (cardAdicionar) {

        container.insertBefore(
            novoCard,
            cardAdicionar
        );

    } else {

        container.appendChild(
            novoCard
        );

    }

}



function excluirServicoCard(botao) {

    const card =
        botao.closest(
            '.servico-card'
        );


    if (!card) {
        return;
    }


    const confirmar =
        confirm(
            'Deseja excluir este serviço?'
        );


    if (!confirmar) {
        return;
    }


    card.remove();

}

//#endregion



//#region PREVIEWS DE AVATAR

function configurarPreviewImagem(
    inputId,
    previewId,
    containerSeletor
) {

    const input =
        document.getElementById(
            inputId
        );


    const preview =
        document.getElementById(
            previewId
        );


    if (!input || !preview) {
        return;
    }


    input.addEventListener(
        'change',
        function () {

            const arquivo =
                input.files[0];


            if (!arquivo) {
                return;
            }


            if (
                !arquivo.type.startsWith(
                    'image/'
                )
            ) {

                alert(
                    'Selecione um arquivo de imagem.'
                );

                input.value = '';

                return;
            }


            const url =
                URL.createObjectURL(
                    arquivo
                );


            preview.src =
                url;


            const container =
                input.closest(
                    containerSeletor
                );


            if (container) {

                container.classList.add(
                    'tem-imagem'
                );

            }


            preview.onload =
                function () {

                    URL.revokeObjectURL(
                        url
                    );

                };

        }
    );

}

//#endregion



//#region PERFIL CONSUMIDOR

function editarConsumidor(botao) {

    const form =
        botao.closest(
            '.consumidor-form-edicao'
        );


    if (!form) {
        return;
    }


    form.classList.add(
        'editando'
    );


    form
        .querySelectorAll(
            '.consumidor-field-left input'
        )
        .forEach(
            function (input) {

                input.removeAttribute(
                    'readonly'
                );

            }
        );


    botao.hidden =
        true;


    const salvar =
        form.querySelector(
            '.consumidor-salvar-alteracoes'
        );


    if (salvar) {

        salvar.hidden =
            false;

    }

}

//#endregion



//#region INFORMAÇÕES DA LOJA

function abrirEdicaoLoja(
    botao,
    nome,
    rua,
    numero,
    cep,
    email,
    telefone,
    cnpj,
    link,
    categoria
) {

    const pagina =
        botao.closest(
            '.info-loja-page'
        );


    if (!pagina) {
        return;
    }


    const form =
        pagina.querySelector(
            '.info-loja-edicao'
        );


    if (!form) {
        return;
    }


    const visualizacao =
        pagina.querySelector(
            '.info-loja-visualizacao'
        );


    if (visualizacao) {

        visualizacao.style.display =
            'none';

    }


    form.style.display =
        'block';


    form.querySelector(
        '.js-editar-loja-nome'
    ).value = nome || '';


    form.querySelector(
        '.js-editar-loja-rua'
    ).value = rua || '';


    form.querySelector(
        '.js-editar-loja-numero'
    ).value = numero || '';


    form.querySelector(
        '.js-editar-loja-cep'
    ).value = cep || '';


    form.querySelector(
        '.js-editar-loja-email'
    ).value = email || '';


    form.querySelector(
        '.js-editar-loja-telefone'
    ).value = telefone || '';


    form.querySelector(
        '.js-editar-loja-cnpj'
    ).value = cnpj || '';


    form.querySelector(
        '.js-editar-loja-link'
    ).value = link || '';


    const selectCategoria =
        form.querySelector(
            '.js-editar-loja-categoria'
        );


    if (selectCategoria) {

        selectCategoria.value =
            categoria || '';

    }

}



function cancelarEdicaoLoja(botao) {

    const form =
        botao.closest(
            '.info-loja-edicao'
        );


    if (!form) {
        return;
    }


    form.style.display =
        'none';


    const pagina =
        form.closest(
            '.info-loja-page'
        );


    if (!pagina) {
        return;
    }


    const visualizacao =
        pagina.querySelector(
            '.info-loja-visualizacao'
        );


    if (visualizacao) {

        visualizacao.style.display =
            '';

    }

}

//#endregion



//#region INFORMAÇÕES DO PRODUTO

function abrirEdicaoProduto(botao) {

    const card =
        botao.closest(
            '.info-produto-card'
        );


    if (!card) {
        return;
    }


    card.classList.add(
        'editando'
    );

}



function cancelarEdicaoProduto(botao) {

    const card =
        botao.closest(
            '.info-produto-card'
        );


    if (!card) {
        return;
    }


    card.classList.remove(
        'editando'
    );

}



function salvarEdicaoProduto(botao) {

    const card =
        botao.closest(
            '.info-produto-card'
        );


    if (!card) {
        return;
    }


    const inputNome =
        card.querySelector(
            '.js-editar-nome'
        );


    const inputPreco =
        card.querySelector(
            '.js-editar-preco'
        );


    const inputDescricao =
        card.querySelector(
            '.js-editar-descricao'
        );


    const nome =
        inputNome.value.trim();


    const preco =
        inputPreco.value.trim();


    const descricao =
        inputDescricao.value.trim();


    if (!nome) {

        alert(
            'Preencha o nome do produto.'
        );

        inputNome.focus();

        return;

    }


    if (!preco) {

        alert(
            'Preencha o preço do produto.'
        );

        inputPreco.focus();

        return;

    }


    card.querySelector(
        '.js-nome'
    ).textContent =
        nome;


    card.querySelector(
        '.js-preco'
    ).textContent =
        'R$ ' + preco;


    card.querySelector(
        '.js-descricao'
    ).textContent =
        descricao ||
        'Sem descrição.';


    card.classList.remove(
        'editando'
    );

}



function excluirProduto(botao) {

    const card =
        botao.closest(
            '.info-produto-card'
        );


    if (!card) {
        return;
    }


    const nome =
        card.querySelector(
            '.js-nome'
        ).textContent.trim();


    const confirmar =
        confirm(
            'Deseja excluir o produto "' +
            nome +
            '"?'
        );


    if (!confirmar) {
        return;
    }


    card.remove();

}

//#endregion



//#region INFORMAÇÕES DO SERVIÇO

function abrirEdicaoServico(botao) {

    const card =
        botao.closest(
            '.info-servico-card'
        );


    if (!card) {
        return;
    }


    card.classList.add(
        'editando'
    );

}



function cancelarEdicaoServico(botao) {

    const card =
        botao.closest(
            '.info-servico-card'
        );


    if (!card) {
        return;
    }


    card.classList.remove(
        'editando'
    );

}

//#endregion



//#region FAVORITOS

function alternarFavorito(botao) {

    if (!botao) {
        return;
    }


    const ativo =
        botao.classList.toggle(
            'favorito-ativo'
        );


    const icone =
        botao.querySelector(
            'i'
        );


    if (!icone) {
        return;
    }


    icone.className =
        ativo
            ? 'bi bi-heart-fill'
            : 'bi bi-heart';

}

//#endregion



//#region INICIALIZAÇÃO

document.addEventListener(
    'DOMContentLoaded',
    function () {

        const themeBtn =
            document.querySelector(
                '.theme-toggle'
            );


        if (themeBtn) {

            const modoEscuro =
                document.body.classList.contains(
                    'dark'
                );


            themeBtn.innerHTML =
                modoEscuro
                    ? '<i class="bi bi-sun-fill" aria-hidden="true"></i> <span class="theme-label">Modo claro</span>'
                    : '<i class="bi bi-moon-fill" aria-hidden="true"></i> <span class="theme-label">Modo escuro</span>';

        }


        document
            .querySelectorAll(
                '.produto-card'
            )
            .forEach(
                prepararProdutoCard
            );


        document
            .querySelectorAll(
                '.servico-card'
            )
            .forEach(
                prepararServicoCard
            );


        configurarPreviewImagem(
            'foto-consumidor',
            'preview-consumidor',
            '.consumidor-avatar'
        );


        configurarPreviewImagem(
            'foto-responsavel',
            'preview-responsavel',
            '.perfil-avatar'
        );


        configurarPreviewImagem(
            'foto-responsavel-produto',
            'preview-responsavel-produto',
            '.produto-avatar'
        );


        configurarPreviewImagem(
            'foto-responsavel-servico',
            'preview-responsavel-servico',
            '.servico-avatar'
        );

    }
);

//#endregion