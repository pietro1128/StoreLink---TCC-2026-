from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'AppStoreLink/index.html')

def perfil(request):
    return render(request, 'AppStoreLink/perfil.html')

def cadastro(request):
    return render(request, 'registration/cadastro.html')

def login(request):
    return render(request, 'registration/login.html')