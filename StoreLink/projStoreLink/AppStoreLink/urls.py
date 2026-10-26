from django.urls import path
from . import views
from AppStoreLink.views import (
    index,
    perfil_loja,
    perfil_consumidor,
    cadastro,
    login,
    recuperar_senha,
    CatAlimentos,
    CatModa,
    CatEsportes,
    CatConstrucao,
    CatSaude,
    CatPets,
    CatAmbiente,
    CatTecnologia,
    CatBeleza,
    CatOutros,
    suporte,
    produtos_loja,
    servicos_loja,
    tutorial
)


urlpatterns = [
    path('', index, name='index'),

    path('perfil-loja/', perfil_loja, name='perfil-loja'),
    
    path('perfil-consumidor/', perfil_consumidor, name='perfil-consumidor'),
    path('perfil-consumidor/editar', views.editar_consumidor, name='editar-consumidor'),

    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login, name='login'),
    path('recuperar-senha/', recuperar_senha, name='recuperar-senha'),

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

    path('suporte/', suporte, name='suporte'),

    path('produtos-loja/', produtos_loja, name='produtos-loja'),
    path('produto/<int:id_produto>/editar/', views.produto_editar, name='produto-editar'),
    path('produto/novo/', views.produto_criar, name='produto-criar'),
    path('produto/<int:id_produto>/excluir/', views.produto_excluir, name='produto-excluir'),

    path('servicos-loja/', servicos_loja,name='servicos-loja'),
    path('servico/<int:id_servico>/excluir/', views.servico_excluir, name='servico-excluir'),

    path('loja/<int:id_loja>/favoritar/', views.favoritar_loja, name='favoritar-loja'),

    path('loja/<int:id_loja>/excluir/', views.loja_excluir, name='loja-excluir'),
    
    path('avaliar/loja/<int:id_alvo>/', views.avaliacao_criar, {'tipo': 'loja'}, name='avaliar-loja'),
    path('avaliar/produto/<int:id_alvo>/', views.avaliacao_criar, {'tipo': 'produto'}, name='avaliar-produto'),
    path('avaliar/servico/<int:id_alvo>/', views.avaliacao_criar, {'tipo': 'servico'}, name='avaliar-servico'),

    path('api/cep/<str:cep>/', views.api_cep, name='api-cep'),
    
    path('logout/', views.logout_view, name='logout'),

    # region PÁGINAS DE INFORMAÇÕES

    path(
        'loja/<int:id_loja>/',
        views.InformacoesLoja,
        name='InformacoesLoja'
    ),
    path('loja/<int:id_loja>/editar/', views.loja_editar, name='loja-editar'),
    path('loja/<int:id_loja>/excluir/', views.loja_excluir, name='loja-excluir'),

    path(
        'loja/<int:id_loja>/produtos/',
        views.InformacoesProduto,
        name='InformacoesProduto'
    ),
    path('loja/<int:id_loja>/editar/', views.produto_editar, name='produto-editar'),
    path('loja/<int:id_loja>/excluir/', views.produto_excluir, name='produto-excluir'),

    path(
        'loja/<int:id_loja>/servicos/',
        views.InformacoesServico,
        name='InformacoesServico'
    ),
    path('loja/<int:id_loja>/editar/', views.servico_editar, name='servico-editar'),
    path('loja/<int:id_loja>/excluir/', views.servico_excluir, name='servico-excluir'),
    

    # endregion

    path('tutorial/', tutorial, name='tutorial'),
]