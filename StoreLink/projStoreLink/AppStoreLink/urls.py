from django.urls import path
from AppStoreLink.views import index, perfil, loginEcadastro

urlpatterns = [
    path('', index, name= 'index'),
    path('perfil', perfil,  name= 'perfil')
    path('loginEcadastro', loginEcadastro,  name= 'loginEcadastro')
]