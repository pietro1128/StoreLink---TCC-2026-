from django.utils.http import url_has_allowed_host_and_scheme
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_POST
from django.contrib import messages # importa mensagens de erro e sucesso
from django.contrib.auth.hashers import make_password, check_password
from AppStoreLink.models import Avaliacao, Usuario, Loja, Endereco, Produto, Servico, LojaFavoritas, TipoUsuario, Categoria# importação das classes em models
from django.contrib.auth.decorators import login_required # @login_required -> usado para privar apenas usuarios loggados
from django.http import HttpResponseForbidden # -> 
import re # importação de Regex: biblioteca de validações
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from AppStoreLink.services import (
    consultar_cep, CepInvalido, CepNaoEncontrado, ServicoCepIndisponivel,
)



def index(request):
    return render(request, 'AppStoreLink/index.html')


# |  Para testar a pagina SEM CONTA, voce precisa transformar
# V  a linha de baixo em um comentario: "#@login_required"
#@login_required
def perfil_loja(request):
    #if request.user.roler != 'admin':
        #return HttpResponseForbidden("Você não tem permição para acessar está página.") 
    
    if request.method == 'POST': # -> verifica se o usuario enviou os dados usando o metodo HTTP 'POST'

        nome = request.POST.get('nome_loja')# -> cria uma variavel puxando o valor do banco
#                                   L> este valor tem que ser exatamente igual ao 'name' em perfil-loja.html
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        cep = request.POST.get('cep')
        endereco = Endereco.objects.create(rua=rua, numero=numero, cep=cep)
        # guarda os valores das variaveis dentro da tabela 'Endereco' que esta guardada dentro da variavel 'endereco'

        email = request.POST.get('email_loja')
        telefone = request.POST.get('telefone_loja')
        cnpj = request.POST.get('cnpj')
        link = request.POST.get('link_loja')
        
        try:
            dados_cep = consultar_cep(cep)
        except CepInvalido:
            messages.error(request, 'CEP inválido. Digite 8 números.')
            return render(request, 'AppStoreLink/perfil-loja.html')
        except CepNaoEncontrado:
            messages.error(request, 'Este CEP não existe.')
            return render(request, 'AppStoreLink/perfil-loja.html')
        except ServicoCepIndisponivel:
            messages.error(request, 'Não foi possível validar o CEP agora. Tente novamente em instantes.')
            return render(request, 'AppStoreLink/perfil-loja.html')

        cep = dados_cep['cep']   # grava só os 8 dígitos, num formato único
        
        # Validações de E-mail para loja:
        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'# -> Argumenta um padrão com characteres finais nos emails
        if not re.match(padrao_email, email): # -> Verifica se estão nos padões argumentados estao coecidindo com as variaveis 
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')# -> cria uma mensagens
            return render(request, 'templates/perfil-loja.html')

        if Loja.objects.filter(email=email).exists():# -> ???.objects.filter(???=???) --> busca valores por filtros argumentados
                                                     # -> .exists() --> verifica se ja existe 
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'templates/perfil-loja.html')

        # Validações de CNPJ:
        padrao_cnpj = r'^.{14,14}$'# ^.{??,??}$ -> diz que o texton precisa ter exatamente o numero de letras argumantadas
        if not re.match(padrao_cnpj, cnpj):
            messages.error(request, 'Este CNPJ deve conter exatamente 14 números.')
            return render(request, 'templates/perfil-loja.html')

        if Loja.objects.filter(cnpj=cnpj).exists():
            messages.error(request, 'Este CNPJ ja foi cadastrado.')
            return render(request, 'templates/perfil-loja.html')

        # Validações de Telefone para loja:
        padrao_telefone = r'^.{11,11}$'
        if not re.match(padrao_telefone, telefone):
            messages.error(request, 'Este número esta incorreto, ele deve ter exatamente 11 números.')
            return render(request, 'templates/perfil-loja.html')

        if Loja.objects.filter(telefone=telefone).exists():
            messages.error(request, 'Este telefone ja foi cadastrado.')
            return render(request, 'templates/perfil-loja.html')

        Loja.objects.create(nome=nome, endereco=endereco, email_loja=email)

    # TODO: trocar pela loja do usuário logado quando existir o vínculo Usuario↔Loja 
    loja = Loja.objects.first()

    return render(request, 'AppStoreLink/perfil-loja.html', {'loja': loja})


def perfil_consumidor(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        messages.error(request, 'Você precisa fazer login para acessar esta página.')
        return redirect('login')

    usuario = get_object_or_404(Usuario, id_categoria=usuario_id)
    loja_fav = LojaFavoritas.objects.filter(id_usuario=usuario).select_related('id_loja')

    return render(
        request,
        'AppStoreLink/perfil-consumidor.html',
        {'chave_perf_consm': usuario, 'loja_fav': loja_fav}
    )


def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        sobrenome = request.POST.get('sobrenome', '').strip() or None # -> 'or None': diz que pode *também* receber valores vazios/'None'
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')
        telefone = request.POST.get('telefone', '').strip() or None
        cpf = request.POST.get('cpf', '').strip() or None
        id_tipo_usuario = request.POST.get('id_tipo_usuario')

        # Validação de e-mail (somente Gmail)
        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        if not re.match(padrao_email, email):
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')
            return render(request, 'registration/cadastro.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'registration/cadastro.html')

        # Validação de senha (mínimo 8 caracteres, maiúscula, minúscula e número)
        padrao_senha = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}'
        """
        >> r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}' <<: Esta linha exige pelo menos (8 char, letra min, letra max e um num)
        >> ^ <<: começa a str
        >> (?=.*...) <<: Lookahead 'verifica se a condição CHAR escrita esta em algum lugar no texto'
        """
        if not re.match(padrao_senha, senha):
            messages.error(request, 'A senha precisa conter no mínimo 8 caracteres, letra maiúscula, minúscula e número.')
            return render(request, 'registration/cadastro.html')

        # Validação de CPF (só roda se o usuário informou, já que é opcional)
        if cpf:
            padrao_cpf = r'^\d{11}$'
            if not re.match(padrao_cpf, cpf):
                messages.error(request, 'O CPF deve ter exatamente 11 números.')
                return render(request, 'registration/cadastro.html')

            if Usuario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'Este CPF já está cadastrado.')
                return render(request, 'registration/cadastro.html')

        usuario = Usuario( # -> Esta criando um objeto a partir do modelo do banco
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            senha=make_password(senha),
            telefone=telefone,
            cpf=cpf,
            id_tipo_usuario_id=id_tipo_usuario,
        )
        usuario.save()# -> Salva os valores concedidos dentro do banco 

        messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')# -> retorna uma mensagem de sucesso caso passe por todos os campos
        return redirect('login')

    return render(request, 'registration/cadastro.html')


@require_GET
def api_cep(request, cep):
    """Endpoint JSON usado pelo front-end para autocompletar o endereço."""
    try:
        endereco = consultar_cep(cep)
    except CepInvalido:
        return JsonResponse({'erro': 'CEP inválido. Digite 8 números.'}, status=400)
    except CepNaoEncontrado:
        return JsonResponse({'erro': 'Este CEP não existe.'}, status=404)
    except ServicoCepIndisponivel:
        return JsonResponse({'erro': 'Não foi possível consultar o CEP agora. Tente novamente.'}, status=503)

    return JsonResponse(endereco)


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')

        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        if not re.match(padrao_email, email):
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')
            return render(request, 'registration/login.html')

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, 'E-mail ou senha inválidos.')
            return render(request, 'registration/login.html')

        if check_password(senha, usuario.senha):
            request.session['usuario_id'] = usuario.id_categoria
            messages.success(request, f'Bem-vindo, {usuario.nome}!')
            return redirect('perfil-consumidor')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'registration/login.html')


def buscar(request):
    query = request.GET.get('q', '').strip()

    lojas = Loja.objects.none()
    produtos = Produto.objects.none()
    servicos = Servico.objects.none()

    if query:
        lojas = Loja.objects.filter(
            Q(nome_loja__icontains=query) |
            Q(id_categoria__tipo_categoria__icontains=query)
        ).select_related('id_endereco', 'id_categoria')

        produtos = Produto.objects.filter(
            Q(nome_produto__icontains=query) |
            Q(descricao__icontains=query) |
            Q(id_categoria__tipo_categoria__icontains=query) |
            Q(id_loja__nome_loja__icontains=query)
        ).select_related('id_loja', 'id_categoria')

        servicos = Servico.objects.filter(
            Q(nome_servico__icontains=query) |
            Q(descricao__icontains=query) |
            Q(id_loja__nome_loja__icontains=query)
        ).select_related('id_loja')

    total_resultados = lojas.count() + produtos.count() + servicos.count()

    contexto = {
        'query': query,
        'lojas': lojas,
        'produtos': produtos,
        'servicos': servicos,
        'total_resultados': total_resultados,
    }

    return render(request, 'AppStoreLink/buscar.html', contexto)


def CatAlimentos(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Alimentos'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Alimentos',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatAlimentos.html', contexto)


def CatModa(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Moda'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Moda',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatModa.html', contexto)


def CatEsportes(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Esportes'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Esportes',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatEsportes.html', contexto)


def CatConstrucao(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Construção'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Construção',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatConstrucao.html', contexto)


def CatSaude(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Saúde'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Saúde',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatSaude.html', contexto)


def CatPets(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Pets'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Pets',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatPets.html', contexto)


def CatAmbiente(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Ambiente'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Ambiente',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatAmbiente.html', contexto)


def CatTecnologia(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Tecnologia'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Tecnologia',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatTecnologia.html', contexto)


def CatBeleza(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Beleza'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Beleza',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatBeleza.html', contexto)


def CatOutros(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Outros'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Outros',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatOutros.html', contexto)


def suporte(request):
    return render(request, 'AppStoreLink/suporte.html')


def _validar_nome_preco(nome, preco_txt):
    """Valida nome e preço. Devolve (lista_de_erros, preco_como_Decimal)."""
    erros = []

    if not nome:
        erros.append('O nome do produto é obrigatório.')
    elif len(nome) > 100:
        erros.append('O nome deve ter no máximo 100 caracteres.')

    preco = None
    try:
        preco = Decimal(preco_txt)
        if not preco.is_finite() or preco <= 0:
            erros.append('O preço deve ser um número maior que zero.')
        elif preco > Decimal('99999999.99'):
            erros.append('O preço informado é alto demais.')
        else:
            preco = preco.quantize(Decimal('0.01'))
    except InvalidOperation:
        erros.append('Informe um preço válido (exemplo: 12,50).')

    return erros, preco


def produtos_loja(request):
    # TODO: quando existir o vínculo Usuário↔Loja, filtrar só os produtos da loja do usuário logado
    produtos = Produto.objects.all()
    categorias = Categoria.objects.all()

    return render(request, 'AppStoreLink/produtos-loja.html', {
        'produtos': produtos,
        'categorias': categorias,
    })

@require_POST
def produto_excluir(request, id_produto):
    produto = get_object_or_404(Produto, id_produto=id_produto)
    nome = produto.nome_produto
    produto.delete()

    messages.success(request, f'O produto "{nome}" foi excluído.')
    return redirect('produtos-loja')


@require_POST
def produto_criar(request):
    nome = request.POST.get('nome_produto', '').strip()
    preco_txt = request.POST.get('preco_produto', '').strip().replace(',', '.')
    descricao = request.POST.get('descricao_produto', '').strip()
    id_categoria = request.POST.get('id_categoria', '')

    erros, preco = _validar_nome_preco(nome, preco_txt)

    # A categoria é obrigatória no model e o POST pode ser forjado, então confere no banco
    categoria = None
    if id_categoria.isdigit():
        categoria = Categoria.objects.filter(id_categoria=id_categoria).first()
    if categoria is None:
        erros.append('Selecione uma categoria válida.')

    # TODO: trocar pela loja do dono logado quando existir o vínculo Usuário↔Loja
    loja = Loja.objects.first()
    if loja is None:
        erros.append('Cadastre uma loja antes de cadastrar produto.')

    if erros:
        for erro in erros:
            messages.error(request, erro)
        return redirect('produtos-loja')

    Produto.objects.create(
        nome_produto=nome,
        preco=preco,
        descricao=descricao or None,
        id_loja=loja,
        id_categoria=categoria,
    )

    messages.success(request, 'Produto cadastrado com sucesso!')
    return redirect('produtos-loja')


@require_POST
def produto_editar(request, id_produto):
    produto = get_object_or_404(Produto, id_produto=id_produto)

    nome = request.POST.get('nome_produto', '').strip()
    preco_txt = request.POST.get('preco_produto', '').strip().replace(',', '.')
    descricao = request.POST.get('descricao_produto', '').strip()

    erros, preco = _validar_nome_preco(nome, preco_txt)

    if erros:
        for erro in erros:
            messages.error(request, erro)
        return redirect('produtos-loja')

    produto.nome_produto = nome
    produto.preco = preco
    produto.descricao = descricao or None
    produto.save()

    messages.success(request, 'Produto atualizado com sucesso!')
    return redirect('produtos-loja')


def servicos_loja(request):
    # ALTERADO: a lista de serviços foi movida para o topo da função.
    # Antes ela ficava só no final, mas agora também precisamos dela no
    # caso de erro de validação (para recarregar a página com os cards).
    servicos = Servico.objects.all()

    if request.method == 'POST':
        nome_servico = request.POST.get('nome_servico', '').strip()  # strip(): tira espaços

        # ALTERADO: antes era só .strip(). Agora o .replace(',', '.') que corrige o erro que falei no resumo
        # (o nome da variável mudou de 'preco' para 'preco_txt' porque aqui
        # ela ainda é TEXTO; o número de verdade fica na variável 'preco')
        preco_txt = request.POST.get('preco', '').strip().replace(',', '.')

        descricao = request.POST.get('descricao', '').strip()

        # NOVO: lista que acumula os erros encontrados. Só salvamos no banco se ela terminar vazia.
        erros = []

        if not nome_servico:
            erros.append('O nome do serviço é obrigatório.')
        elif len(nome_servico) > 100:
            erros.append('O nome deve ter no máximo 100 caracteres.')

        #Decimal é o tipo mais recomendado para dinheiro, e não o float  
        preco = None
        try:
            preco = Decimal(preco_txt)  # levanta InvalidOperation se for "abc" ou vazio

            # is_finite() barra valores como "nan" e "infinity", que o Decimal
            # aceita como texto mas não servem como preço.
            if not preco.is_finite() or preco <= 0:
                erros.append('O preço deve ser um número maior que zero.')
            # 99999999.99 é o maior valor que cabe em DecimalField(10, 2)
            elif preco > Decimal('99999999.99'):
                erros.append('O preço informado é alto demais.')
            else:
                # força exatamente 2 casas decimais (6.7 vira 6.70)
                preco = preco.quantize(Decimal('0.01'))
        except InvalidOperation:
            erros.append('Informe um preço válido (exemplo: 50,00).')


        # MANTIDO da versão original: pega a primeira loja do banco.
        # Atenção: isso coloca TODO serviço na mesma loja, não importa quem cadastrou. É uma limitação conhecida, só dá para resolver quando existir o vínculo Usuario -> Loja no banco.
        # TODO: trocar pela loja do usuário logado.
        
        loja = Loja.objects.first()
        if loja is None:
            erros.append('Cadastre uma loja antes de cadastrar serviço.')

        # NOVO: se achou algum problema, mostra as mensagens e NÃO salva.
        # Usamos render (e não redirect) para recarregar a página direto.
        if erros:
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'AppStoreLink/servicos-loja.html', {'servicos': servicos})

        Servico.objects.create(
            nome_servico=nome_servico,
            preco=preco,  # ALTERADO: agora é um Decimal, não mais o texto cru
            # ALTERADO: o campo descricao aceita nulo no model; texto vazio
            # ('') é salvo como None para manter o banco consistente.
            descricao=descricao or None,
            id_loja=loja,
        )

        messages.success(request, 'Serviço cadastrado com sucesso!')
        return redirect('servicos-loja')  # redirect evita reenviar o form ao apertar F5

    # IMPORTANTE: este return fica alinhado com o 'if' de cima, FORA dele.
    # Se ele ficar dentro do 'if request.method == POST', a página não abre
    # por GET e dá "view retornou None".
    return render(request, 'AppStoreLink/servicos-loja.html', {'servicos': servicos})

# ============================================================================
# RESUMO DAS ALTERAÇÕES 
#
# Problema: quando cadastra um serviço com preço "6,70", o sistema dava erro
# de validação (ValidationError) e mostrava a tela de erro do Django.
#
# Causa: o preço ia direto do formulário para o banco como TEXTO. O banco
# espera um número decimal com ponto ("6.70"), e o brasileiro digita com
# vírgula ("6,70"). Preço vazio ou com letras quebrava do mesmo jeito.
#
# O que foi feito:
#   1. Converter o preço de texto para número (Decimal) antes de salvar.
#   2. Aceitar vírgula e ponto no preço.
#   3. Validar nome e preço, mostrando mensagem de erro em vez de quebrar.
#   4. Juntar todas as mensagens de erro numa lista (o usuário vê todos os
#      problemas de uma vez, não um por vez).
# ============================================================================

@require_POST
def servico_excluir(request, id_servico):
    servico = get_object_or_404(Servico, id_servico=id_servico)
    nome = servico.nome_servico
    servico.delete()

    messages.success(request, f'O serviço "{nome}" foi excluído.')
    return redirect('servicos-loja')

@require_POST # -> so deixa executar a função se a requisição usar o metodo HTTP 'POST'
def favoritar_loja(request, id_loja):
    
    usuario_id = request.session.get('usuario_id') # -> consulta a sessão para saber qual usuario esta conectado
    if not usuario_id: # -> verifica se esta desconectado
        messages.error(request, 'Você precisa fazer login para favorizar uma loja.')
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, id_categoria=usuario_id) # -> procura o usuario registrado no banco e guarda o valor na variavel 'usuario'
    loja = get_object_or_404(Loja, id_loja=id_loja)
    
    favorita, criada = LojaFavoritas.objects.get_or_create( # -> verifica de o usuario ja favoritou ou não a loja
        id_usuario=usuario, # -> indica o 'usuario' que favoritou a 'loja'
        id_loja=loja,
    )
    
    if not criada:
        favorita.delete() # -> remove o favorito quando apertar no botao de uma loja ja favoritada
        #           L> '.delete()': deleta o registro do banco
    return redirect(request.META.get('HTTP_REFERER', 'perfil-consumidor')) # -> redireciona para a pagina que veio, caso contrario ele redireciona para 'perfil-consumidor'

@require_POST
def loja_excluir(request, id_loja):
    loja = get_object_or_404(Loja, id_loja=id_loja)

    # TODO: quando existir o vínculo Usuario↔Loja, conferir aqui se o usuário
    # logado é o dono da loja antes de permitir a exclusão.

    nome = loja.nome_loja
    endereco = loja.id_endereco

    # atomic: ou apaga tudo, ou não apaga nada (se der erro no meio, desfaz)
    with transaction.atomic():
        loja.delete()  # CASCADE apaga produtos, serviços e favoritos da loja

        # Limpa o endereço órfão, mas só se nenhuma outra loja usar o mesmo
        if not Loja.objects.filter(id_endereco=endereco).exists():
            endereco.delete()

    messages.success(request, f'A loja "{nome}" foi excluída.')
    return redirect('index')


def _voltar(request):
    """Volta para a página de onde veio o formulário"""
    destino = request.META.get('HTTP_REFERER')
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return redirect(destino)
    return redirect('index')


@require_POST
def avaliacao_criar(request, tipo, id_alvo):
    # tipo vem da URL ('loja', 'produto' ou 'servico'): diz qual FK preencher
    modelos = {
        'loja': (Loja, 'id_loja'),
        'produto': (Produto, 'id_produto'),
        'servico': (Servico, 'id_servico'),
    }
    modelo, campo = modelos[tipo]

    # Quem avalia vem da sessão do login manual
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Você precisa fazer login para avaliar.')
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=usuario_id)#???(pk): funciona mesmo com as chaves primárias customizadas (id_loja, id_produto...), então não depende do nome delas.

    alvo = get_object_or_404(modelo, pk=id_alvo)

    comentario = request.POST.get('comentario', '').strip()
    try:
        nota = int(request.POST.get('nota', ''))
    except ValueError:
        nota = None

    erros = []
    if nota is None or not 1 <= nota <= 5:
        erros.append('A nota deve ser um número de 1 a 5.')
    if len(comentario) > 1000:
        erros.append('O comentário deve ter no máximo 1000 caracteres.')

    if erros:
        for erro in erros:
            messages.error(request, erro)
        return _voltar(request)

    # update_or_create: se este usuário já avaliou este alvo, atualiza;
    # se não, cria. Assim cada pessoa tem no máximo 1 avaliação por alvo.
    Avaliacao.objects.update_or_create(
        id_usuario=usuario,
        **{campo: alvo},
        defaults={'nota': nota, 'comentario': comentario or None},
    )

    messages.success(request, 'Avaliação salva com sucesso!')
    return _voltar(request)