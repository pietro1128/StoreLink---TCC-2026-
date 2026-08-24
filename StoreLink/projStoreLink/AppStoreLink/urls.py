from django.urls import path
from AppStoreLink.views import index, perfil

urlpatterns = [
    path('', index, name= 'index'),
    path('perfil', perfil,  name= 'perfil')
]