from django.urls import path
from AppStoreLink.views import index, perfil, cadastro, login

urlpatterns = [
    #pagina inicial
    path('', index, name= 'index'),

    #paginas de perfil
    path('perfil', perfil,  name= 'perfil'),

    #paginas de Autenticação
    path('cadastro', cadastro,  name= 'cadastro'),
    path('login', login,  name= 'login'),
]