from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from AppStoreLink.models import Usuario, Loja, Endereco, Produto, Servico, LojaFavoritas
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'AppStoreLink/index.html')


# |  Para testar a pagina SEM CONTA, voce precisa transformar
# V  a linha de baixo em um comentario: "#@login_required"
#@login_required
def perfil_loja(request):
    if request.method == 'POST':
        usuario.nome = request.POST.get('nome', '')
        usuario.sobrenome = request.POST.get('sobrenome', '')
        usuario.save()
        
    elif request.method == 'POST':
        loja.nome_loja = request.POST.get('nome_loja', '')
        loja.save()
        
        endereco.rua = request.POST.get('rua', '')
        endereco.numero_estabelecimento = request.POST.get('numero', '')
        endereco.cep = request.POST.get('cep', '')
        endereco.save()
        
        loja.email_loja = request.POST.get('email_loja', '')
        loja.telefone_loja = request.POST.get('telefone_loja', '')
        loja.cnpj = request.POST.get('cnpj', '')
        loja.link = request.POST.get('link_loja', '')
        loja.save()
        

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


# >>>>>>>>>>>>> ERRO <<<<<<<<<<<<<<<<<
def cadastro(request):
    if request.method == 'POST':
        usuario.nome = request.POST.get('nome', '')
        usuario.email = request.POST.get('email', '')
        usuario.senha = request.POST.get('senha', '')
        usuario.save()
    
    usuario = Usuario.objects.all()

    return render(request, 'registration/cadastro.html')


def login(request):
    usuario = Usuario.objects.all()
    loja = Loja.objects.all()

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