from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages # importa comandos para mensagens de erro
from django.contrib.auth.hashers import make_password, check_password
from AppStoreLink.models import Usuario, Loja, Endereco, Produto, Servico, LojaFavoritas, TipoUsuario
from django.contrib.auth.decorators import login_required
import re # importa o regex (uma biblioteca para validações)


def index(request):
    return render(request, 'AppStoreLink/index.html')


# |  Para testar a pagina SEM CONTA, voce precisa transformar
# V  a linha de baixo em um comentario: "#@login_required"
#@login_required
def perfil_loja(request):
    if request.method == 'POST': 

        nome = request.POST.get('nome_loja')  # -> Cria uma variavel puxando o valor do bando
        #                          L> este campo ('nome-loja'): tem que ser igual ao 'name' do html
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        cep = request.POST.get('cep')
        endereco = Endereco.objects.create(rua = rua, numero = numero, cep = cep)# -> 

        email = request.POST.get('email_loja')
        telefone = request.POST.get('telefone_loja')
        cnpj = request.POST.get('cnpj')
        #foto_estabelecimento = request.POST.get('')
        link = request.POST.get('link_loja')
        Loja.objects.create(nome = nome, endereco = endereco, email_loja = email )

    loja = Loja.objects.all()
    usuario = Usuario.objects.all()
    endereco = Endereco.objects.all()
    produto = Produto.objects.all()
    servico = Servico.objects.all()

    return render(request, 'AppStoreLink/perfil-loja.html')


def perfil_consumidor(request):
    usuario = Usuario.objects.all()
    loja_fav = LojaFavoritas.objects.all()

    return render(
        request,
        'AppStoreLink/perfil-consumidor.html',
        {'chave_perf_consm': usuario}
    )


def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome').strip()
        #sobrenome = request.POST.get('sobrenome').strip()
        email = request.POST.get('email').strip()
        senha = request.POST.get('senha')
        #telefone = request.POST.get('telefone').strip()
        #cpf = request.POST.get('cpf').strip()
        #id_tipo_usuario = request.POST.get('id_tipo_usuario')  # ex: valor vindo de um <select>    

# Validações de E-mail para cadastro:
        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$' # -> Argumenta um padrão com characteres finais nos emails
        if not re.match(padrao_email, email): # -> Verifica se estão nos padões argumentados
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')
            return render(request, 'registration/cadastro.html')
        
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'registration/cadastro.html')
        
# Validações de Senha para cadastro:

# Validações de CPF para cadastro:
        #if Usuario.objects.filter(cpf=cpf).exists():
         #   messages.error(request, 'Este CPF já está cadastrado.')
          #  return render(request, 'registration/cadastro.html')


        usuario = Usuario(
            nome=nome,
            #sobrenome=sobrenome,
            email=email,
            senha=make_password(senha),  # ← aqui a senha vira um hash, nunca texto puro
            #telefone=telefone,
            #cpf=cpf,
            #id_tipo_usuario_id=id_tipo_usuario,
        )
        usuario.save()

        messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
        return redirect('login')

    return render(request, 'registration/cadastro.html')

    
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, 'E-mail ou senha inválidos.')
            return render(request, 'registration/login.html')

        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'# -> Argumenta um padrão com characteres finais nos emails
        if not re.match(padrao_email, email): # -> Verifica se estão nos padões argumentados
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')
            return render(request, 'registration/login.html')
                
        if check_password(senha, usuario.senha):
            # Login bem-sucedido: guarda o ID do usuário na sessão
            request.session['usuario_id'] = usuario.id_categoria
            messages.success(request, f'Bem-vindo, {usuario.nome}!')
            return redirect('index')
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
        ).select_related('id.loja', 'id_categoria')

        servicos = Servico.objects.filter(
            Q(nome_servico__icontains=query) |
            Q(descricao__icontains=query) |
            Q(id_loja__nome_loja__icontains=query)
        ).select_related('id.loja')

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

    return render(
        request,
        'AppStoreLink/CatAlimentos.html',
        contexto
    )


def CatModa(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Moda'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Moda',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatModa.html',
        contexto
    )


def CatEsportes(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Esportes'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Esportes',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatEsportes.html',
        contexto
    )
def CatConstrucao(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Construção'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Construção',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatConstrucao.html',
        contexto
    )


def CatSaude(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Saúde'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Saúde',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatSaude.html',
        contexto
    )


def CatPets(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Pets'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Pets',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatPets.html',
        contexto
    )


def CatAmbiente(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Ambiente'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Ambiente',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatAmbiente.html',
        contexto
    )


def CatTecnologia(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Tecnologia'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Tecnologia',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatTecnologia.html',
        contexto
    )


def CatBeleza(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Beleza'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Beleza',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatBeleza.html',
        contexto
    )


def CatOutros(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Outros'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Outros',
        'lojas': lojas,
    }

    return render(
        request,
        'AppStoreLink/CatOutros.html',
        contexto
    )