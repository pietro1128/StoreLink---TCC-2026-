from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages # importa mensagens de erro e sucesso
from django.contrib.auth.hashers import make_password, check_password
from AppStoreLink.models import Usuario, Loja, Endereco, Produto, Servico, LojaFavoritas, TipoUsuario # importação das classes em models
from django.contrib.auth.decorators import login_required # @login_required -> usado para privar apenas usuarios loggados
from django.http import HttpResponseForbidden # -> 
import re # importação de Regex: biblioteca de validações


def index(request):
    return render(request, 'AppStoreLink/index.html')


# |  Para testar a pagina SEM CONTA, voce precisa transformar
# V  a linha de baixo em um comentario: "#@login_required"
#@login_required
def perfil_loja(request):
    #if request.user.roler != 'admin':
        #return HttpResponseForbidden("Você não tem permição para acessar está página.") 
    
    if request.method == 'POST':

        nome = request.POST.get('nome_loja')# -> cria uma variavel puxando o valor do banco
#                                   L> este valor tem que ser exatamente igual ao 'name' em perfil-loja.html
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        cep = request.POST.get('cep')
        endereco = Endereco.objects.create(rua=rua, numero=numero, cep=cep)
        # guarda os valores das variaveis dentro da tabela 'Endereco' que esta guardada dentro da variavel 'endereco'

        email = request.POST.get('email_loja')
        telefone = request.POST.get('telefone_loja')
        cnpj = request.POST.get('cnpj')
        link = request.POST.get('link_loja')

        # Validações de E-mail para loja:
        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'# -> Argumenta um padrão com characteres finais nos emails
        if not re.match(padrao_email, email): # -> Verifica se estão nos padões argumentados estao coecidindo com as variaveis 
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')# -> cria uma mensagens
            return render(request, 'templates/perfil-loja.html')

        if Loja.objects.filter(email=email).exists():# -> ???.objects.filter(???=???) --> busca valores por filtros argumentados
                                                     # -> .exists() --> verifica se ja existe 
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'templates/perfil-loja.html')

        # Validações de CNPJ:
        padrao_cnpj = r'^.{14,14}$'# ^.{??,??}$ -> diz que o texton precisa ter exatamente o numero de letras argumantadas
        if not re.match(padrao_cnpj, cnpj):
            messages.error(request, 'Este CNPJ deve conter exatamente 14 números.')
            return render(request, 'templates/perfil-loja.html')

        if Loja.objects.filter(cnpj=cnpj).exists():
            messages.error(request, 'Este CNPJ ja foi cadastrado.')
            return render(request, 'templates/perfil-loja.html')

        # Validações de CEP para loja:
        padrao_cep = r'^.{8,8}$'
        if not re.match(padrao_cep, cep):
            messages.error(request, 'Este CEP está incorreto, ele deve ter exatamente 8 números.')
            return render(request, 'templates/perfil-loja.html')

        # Validações de Telefone para loja:
        padrao_telefone = r'^.{11,11}$'
        if not re.match(padrao_telefone, telefone):
            messages.error(request, 'Este número esta incorreto, ele deve ter exatamente 11 números.')
            return render(request, 'templates/perfil-loja.html')

        if Loja.objects.filter(telefone=telefone).exists():
            messages.error(request, 'Este telefone ja foi cadastrado.')
            return render(request, 'templates/perfil-loja.html')

        Loja.objects.create(nome=nome, endereco=endereco, email_loja=email)

    loja = Loja.objects.all()# -> '???.objects.all()': Busca todos os registros salvos no banco sobre a tabela argumentada
    usuario = Usuario.objects.all()
    endereco = Endereco.objects.all()
    produto = Produto.objects.all()
    servico = Servico.objects.all()

    return render(request, 'AppStoreLink/perfil-loja.html')


def perfil_consumidor(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        messages.error(request, 'Você precisa fazer login para acessar esta página.')
        return redirect('login')

    usuario = get_object_or_404(Usuario, id_categoria=usuario_id)
    loja_fav = LojaFavoritas.objects.filter(id_usuario=usuario).select_related('id_loja')

    return render(
        request,
        'AppStoreLink/perfil-consumidor.html',
        {'chave_perf_consm': usuario, 'loja_fav': loja_fav}
    )


def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        sobrenome = request.POST.get('sobrenome', '').strip() or None # -> 'or None': diz que pode *também* receber valores vazios/'None'
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')
        telefone = request.POST.get('telefone', '').strip() or None
        cpf = request.POST.get('cpf', '').strip() or None
        id_tipo_usuario = request.POST.get('id_tipo_usuario')

        # Validação de e-mail (somente Gmail)
        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        if not re.match(padrao_email, email):
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')
            return render(request, 'registration/cadastro.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'registration/cadastro.html')

        # Validação de senha (mínimo 8 caracteres, maiúscula, minúscula e número)
        padrao_senha = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}'
        """
        >> r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}' <<: Esta linha exige pelo menos (8 char, letra min, letra max e um num)
        >> ^ <<: começa a str
        >> (?=.*...) <<: Lookahead 'verifica se a condição CHAR escrita esta em algum lugar no texto'
        """
        if not re.match(padrao_senha, senha):
            messages.error(request, 'A senha precisa conter no mínimo 8 caracteres, letra maiúscula, minúscula e número.')
            return render(request, 'registration/cadastro.html')

        # Validação de CPF (só roda se o usuário informou, já que é opcional)
        if cpf:
            padrao_cpf = r'^\d{11}$'
            if not re.match(padrao_cpf, cpf):
                messages.error(request, 'O CPF deve ter exatamente 11 números.')
                return render(request, 'registration/cadastro.html')

            if Usuario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'Este CPF já está cadastrado.')
                return render(request, 'registration/cadastro.html')

        usuario = Usuario( # -> Esta criando um objeto a partir do modelo do banco
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            senha=make_password(senha),
            telefone=telefone,
            cpf=cpf,
            id_tipo_usuario_id=id_tipo_usuario,
        )
        usuario.save()# -> Salva os valores concedidos dentro do banco 

        messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')# -> retorna uma mensagem de sucesso caso passe por todos os campos
        return redirect('login')

    return render(request, 'registration/cadastro.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')

        padrao_email = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        if not re.match(padrao_email, email):
            messages.error(request, 'O campo E-mail deve ser um Gmail válido (exemplo: email@gmail.com).')
            return render(request, 'registration/login.html')

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, 'E-mail ou senha inválidos.')
            return render(request, 'registration/login.html')

        if check_password(senha, usuario.senha):
            request.session['usuario_id'] = usuario.id_categoria
            messages.success(request, f'Bem-vindo, {usuario.nome}!')
            return redirect('perfil-consumidor')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'registration/login.html')


def buscar(request):
    query = request.GET.get('q', '').strip()

    lojas = Loja.objects.none()
    produtos = Produto.objects.none()
    servicos = Servico.objects.none()

    if query:
        lojas = Loja.objects.filter(
            Q(nome_loja__icontains=query) |
            Q(id_categoria__tipo_categoria__icontains=query)
        ).select_related('id_endereco', 'id_categoria')

        produtos = Produto.objects.filter(
            Q(nome_produto__icontains=query) |
            Q(descricao__icontains=query) |
            Q(id_categoria__tipo_categoria__icontains=query) |
            Q(id_loja__nome_loja__icontains=query)
        ).select_related('id_loja', 'id_categoria')

        servicos = Servico.objects.filter(
            Q(nome_servico__icontains=query) |
            Q(descricao__icontains=query) |
            Q(id_loja__nome_loja__icontains=query)
        ).select_related('id_loja')

    total_resultados = lojas.count() + produtos.count() + servicos.count()

    contexto = {
        'query': query,
        'lojas': lojas,
        'produtos': produtos,
        'servicos': servicos,
        'total_resultados': total_resultados,
    }

    return render(request, 'AppStoreLink/buscar.html', contexto)


def CatAlimentos(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Alimentos'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Alimentos',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatAlimentos.html', contexto)


def CatModa(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Moda'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Moda',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatModa.html', contexto)


def CatEsportes(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Esportes'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Esportes',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatEsportes.html', contexto)


def CatConstrucao(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Construção'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Construção',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatConstrucao.html', contexto)


def CatSaude(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Saúde'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Saúde',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatSaude.html', contexto)


def CatPets(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Pets'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Pets',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatPets.html', contexto)


def CatAmbiente(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Ambiente'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Ambiente',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatAmbiente.html', contexto)


def CatTecnologia(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Tecnologia'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Tecnologia',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatTecnologia.html', contexto)


def CatBeleza(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Beleza'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Beleza',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatBeleza.html', contexto)


def CatOutros(request):
    lojas = Loja.objects.filter(
        id_categoria__tipo_categoria='Outros'
    ).select_related('id_endereco', 'id_categoria')

    contexto = {
        'categoria': 'Outros',
        'lojas': lojas,
    }

    return render(request, 'AppStoreLink/CatOutros.html', contexto)


def suporte(request):
    return render(request, 'AppStoreLink/suporte.html')


def produtos_loja(request):
    return render(request, 'AppStoreLink/produtos-loja.html')


def servicos_loja(request):
    return render(request, 'AppStoreLink/servicos-loja.html')