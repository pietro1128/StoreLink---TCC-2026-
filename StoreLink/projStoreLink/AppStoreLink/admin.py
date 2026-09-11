from django.contrib import admin
from .models import Usuario, Loja, Endereco, Produto, Servico, LojaFavoritas
#colocar o decorator
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    pass

@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    pass

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    pass

#colocar o decorator
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    pass

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    pass

@admin.register(LojaFavoritas)
class LojaFavoritasAdmin(admin.ModelAdmin):
    pass