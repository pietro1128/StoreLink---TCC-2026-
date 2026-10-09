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

        btn.textContent =
            modoEscuro
                ? '☀️ Modo claro'
                : '🌙 Modo escuro';

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


    // Produto que já veio com imagem
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


    // Abrir seletor de arquivo
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


    // Preview
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
            ✕
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
                📷 Adicionar imagem
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
                ✎
            </button>

        </div>


        <div class="produto-card-conteudo">

            <button
                type="button"
                class="produto-editar-info"
                title="Editar informações"
                aria-label="Editar informações"
            >
                ✎
            </button>


            <label>
                Nome do produto:
            </label>

            <input
                type="text"
                placeholder="Nome do produto"
            >


            <label>
                Preço do produto:
            </label>

            <input
                type="text"
                placeholder="R$ 00,00"
            >


            <label>
                Descrição do produto:
            </label>

            <textarea
                placeholder="Descrição do produto..."
            ></textarea>

        </div>

    `;


    return card;
}



function adicionarProduto() {

    const container =
        document.getElementById(
            'produtoCards'
        )
        ||
        document.querySelector(
            '.produto-cards-scroll'
        );


    if (!container) {

        console.error(
            'Não encontrei o container dos produtos.'
        );

        return;
    }


    const cardAdicionar =
        document.getElementById(
            'produtoCriarCard'
        )
        ||
        container.querySelector(
            '.produto-criar-card'
        );


    const novoCard =
        criarProdutoCard();


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


    prepararProdutoCard(
        novoCard
    );


    const campoNome =
        novoCard.querySelector(
            '.produto-card-conteudo input'
        );


    if (campoNome) {

        campoNome.focus();

    }


    novoCard.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center'
    });

}



function excluirProdutoCard(botao) {

    if (!botao) {
        return;
    }


    const card =
        botao.closest(
            '.produto-card'
        );


    if (!card) {
        return;
    }


    const confirmou =
        confirm(
            'Deseja realmente excluir este produto?'
        );


    if (!confirmou) {
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
            ✕
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
                📷 Adicionar imagem
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
                ✎
            </button>

        </div>


        <div class="servico-card-conteudo">

            <button
                type="button"
                class="servico-editar-info"
                title="Editar informações"
                aria-label="Editar informações"
            >
                ✎
            </button>


            <label>
                Nome do serviço:
            </label>

            <input
                type="text"
                placeholder="Nome do serviço"
            >


            <label>
                Preço do serviço:
            </label>

            <input
                type="text"
                placeholder="R$ 00,00"
            >


            <label>
                Descrição do serviço:
            </label>

            <textarea
                placeholder="Descrição do serviço..."
            ></textarea>

        </div>

    `;


    return card;
}



function adicionarServico() {

    const container =
        document.getElementById(
            'servicoCards'
        )
        ||
        document.querySelector(
            '.servico-cards-scroll'
        );


    if (!container) {

        console.error(
            'Não encontrei o container dos serviços.'
        );

        return;
    }


    const cardAdicionar =
        document.getElementById(
            'servicoCriarCard'
        )
        ||
        container.querySelector(
            '.servico-criar-card'
        );


    const novoCard =
        criarServicoCard();


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


    prepararServicoCard(
        novoCard
    );


    const campoNome =
        novoCard.querySelector(
            '.servico-card-conteudo input'
        );


    if (campoNome) {

        campoNome.focus();

    }


    novoCard.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center'
    });

}



function excluirServicoCard(botao) {

    if (!botao) {
        return;
    }


    const card =
        botao.closest(
            '.servico-card'
        );


    if (!card) {
        return;
    }


    const confirmou =
        confirm(
            'Deseja realmente excluir este serviço?'
        );


    if (!confirmou) {
        return;
    }


    card.remove();
}

//#endregion



//#region AVATAR PRODUTO

function prepararAvatarProduto() {

    const input =
        document.getElementById(
            'foto-responsavel-produto'
        );


    const preview =
        document.getElementById(
            'preview-responsavel-produto'
        );


    const avatar =
        document.querySelector(
            '.produto-avatar'
        );


    if (
        !input ||
        !preview ||
        !avatar
    ) {
        return;
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
                    'Selecione uma imagem.'
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


            avatar.classList.add(
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

//#endregion



//#region AVATAR SERVIÇO

function prepararAvatarServico() {

    const input =
        document.getElementById(
            'foto-responsavel-servico'
        );


    const preview =
        document.getElementById(
            'preview-responsavel-servico'
        );


    const avatar =
        document.querySelector(
            '.servico-avatar'
        );


    if (
        !input ||
        !preview ||
        !avatar
    ) {
        return;
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
                    'Selecione uma imagem.'
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


            avatar.classList.add(
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

//#endregion



//#region INICIALIZAÇÃO

document.addEventListener(
    'DOMContentLoaded',
    function () {


        //#region TEMA

        const themeBtn =
            document.querySelector(
                '.theme-toggle'
            );


        if (
            localStorage.getItem('theme')
            ===
            'dark'
        ) {

            document.body.classList.add(
                'dark'
            );


            if (themeBtn) {

                themeBtn.textContent =
                    '☀️ Modo claro';

            }

        }

        //#endregion



        //#region PRODUTOS

        document
            .querySelectorAll(
                '.produto-card'
            )
            .forEach(function (card) {

                prepararProdutoCard(
                    card
                );

            });


        prepararAvatarProduto();

        //#endregion



        //#region SERVIÇOS

        document
            .querySelectorAll(
                '.servico-card'
            )
            .forEach(function (card) {

                prepararServicoCard(
                    card
                );

            });


        prepararAvatarServico();

        //#endregion

    }
);

//#endregion