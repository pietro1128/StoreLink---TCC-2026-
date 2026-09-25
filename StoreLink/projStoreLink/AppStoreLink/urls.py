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
    CatEsportes,
    CatConstrucao,
    CatSaude,
    CatPets,
    CatAmbiente,
    CatTecnologia,
    CatBeleza,
    CatOutros
)


urlpatterns = [
    path('', index, name='index'),

    path('perfil-loja/', perfil_loja, name='perfil-loja'),
    path('perfil-consumidor/', perfil_consumidor, name='perfil-consumidor'),

    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login, name='login'),

    path('buscar/', views.buscar, name='buscar'),

    path('CatAlimentos/', CatAlimentos, name='CatAlimentos'),

    path('CatModa/', CatModa, name='CatModa'),

    path('CatEsportes/', CatEsportes, name='CatEsportes'),

    path('CatConstrucao/', CatConstrucao, name='CatConstrucao'),

    path('CatSaude/', CatSaude, name='CatSaude'),

    path('CatPets/', CatPets, name='CatPets'),

    path('CatAmbiente/', CatAmbiente, name='CatAmbiente'),

    path('CatTecnologia/', CatTecnologia, name='CatTecnologia'),

    path('CatBeleza/', CatBeleza, name='CatBeleza'),

    path('CatOutros/', CatOutros, name='CatOutros'),
]