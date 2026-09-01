from django.urls import path
from AppStoreLink.views import index, perfil_loja, perfil_consumidor, cadastro, login

urlpatterns = [
    #pagina inicial
    path('', index, name= 'index'),

    #paginas de perfil
    path('perfil-loja', perfil_loja,  name= 'perfil-loja'),
    path('perfil-consumidor', perfil_consumidor,  name= 'perfil-consumidor'),

    #paginas de Autenticação
    path('cadastro', cadastro,  name= 'cadastro'),
    path('login', login,  name= 'login'),
]