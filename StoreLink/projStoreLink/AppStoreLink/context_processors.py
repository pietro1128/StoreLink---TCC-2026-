"""
Essa pagina foi criada pois, o Django precisa de um lugar para 
importar a função 'usuario_logado', esta pagina faz o Django chamar
essa função a cada renderização de template.

o nome 'context_processors.py' e um nome padrão dentro da comunidade
Django, entao qualquer outro que abrir o projeto sabera onde procurar
"""

from AppStoreLink.models import Usuario

def usuario_logado(request): # -> define a função que chama a cada renderização
    usuario_id = request.session.get('usuario_id') # -> essa linha define que um 'usuario_id' e logado, e nao logado e um 'None'
    usuario = Usuario.objects.filter(pk=usuario_id).first() if usuario_id else None # -> verifica se o 'usuario_id' tem valor, caso nao, retorna 'None'
    return {'usuario_logado': usuario} # -> a chave 'usuario_logado' vira o nome da var. em templates
                                       # -> e 'usuario' e o conteudo dessa var.