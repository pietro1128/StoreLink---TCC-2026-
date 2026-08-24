from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(renquest, 'AppStoreLink/index.html')

def perfil(request):
    return render(renquest, 'AppStoreLink/perfil.html')
