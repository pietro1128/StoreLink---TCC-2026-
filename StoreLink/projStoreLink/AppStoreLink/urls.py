from django.urls import path
from AppStoreLink.views import index, perfil, cadastro

urlpatterns = [
    path('', index, name= 'index'),
    path('perfil', perfil,  name= 'perfil')
    path('cadastro', cadastro,  name= 'cadastro')
]