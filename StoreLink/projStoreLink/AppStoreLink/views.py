from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from AppStoreLink.models import Usuario, Loja, Endereco, Produto, Servico, LojaFavoritas
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'AppStoreLink/index.html')

@login_required
def perfil_loja(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

    loja = Loja.objects.all()
    usuario = Usuario.objects.all()
    endereco = Endereco.objects.all()
    produto = Produto.objects.all()
    servico = Servico.objects.all()
    return render(request, 'AppStoreLink/perfil-loja.html')

def perfil_consumidor(request):
    usuario = Usuario.objects.all()
    loja_fav = LojaFavoritas.objects.all()
    return render(request, 'AppStoreLink/perfil-consumidor.html', {'chave_perf_consm': usuario})

def cadastro(request):
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