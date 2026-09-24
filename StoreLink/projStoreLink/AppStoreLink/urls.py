from django.urls import path
from . import views
from AppStoreLink.views import (
    index,
    perfil_loja,
    perfil_consumidor,
    cadastro,
    login,
    CatAlimentos,
    CatModa,
    CatEsportes
)


urlpatterns = [
    # pagina inicial
    path('', index, name='index'),

    # paginas de perfil
    path('perfil-loja/', perfil_loja, name='perfil-loja'),
    path('perfil-consumidor/', perfil_consumidor, name='perfil-consumidor'),

    # paginas de Autenticação
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login, name='login'),

    # campo de busca
    path('buscar/', views.buscar, name='buscar'),

    # categoria Alimentos
    path('CatAlimentos/', CatAlimentos, name='CatAlimentos'),

    # categoria Moda
    path('CatModa/', CatModa, name='CatModa'),

    # categoria Esportes
    path('CatEsportes/', CatEsportes, name='CatEsportes'),
]