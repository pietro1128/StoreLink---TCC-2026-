from django.shortcuts import render
from django.http import HttpResponse
from AppStoreLink.models import Usuario

#ERRO ------->


def index(request):
    return render(request, 'AppStoreLink/index.html')

def perfil_loja(request):
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