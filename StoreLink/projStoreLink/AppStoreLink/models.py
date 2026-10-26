from django.db import models
import os
import uuid
from django.core.exceptions import ValidationError
from PIL import Image
# Create your models here.

#=======================================================================

# NÃO RENOMEAR, NEM MOVER AS FUNÇÕES validar_foto E caminho_foto_usuario

#======================================================================= 

# Tamanho e formato do arquivo para foto
FOTO_TAMANHO_MAXIMO = 2 * 1024 * 1024    # 2 MB
FOTO_EXTENSOES = ('.jpg', '.jpeg', '.png', '.webp')
FOTO_FORMATOS = ('JPEG', 'PNG', 'WEBP')
FOTO_LADO_MAXIMO = 4000                  # pixels


def validar_foto(arquivo):
    """Levanta ValidationError se a foto não atender às regras do sistema."""
    # Foto que já está salva não é revalidada (evita erro se o arquivo sumir do disco).
    if getattr(arquivo, '_committed', False):
        return

    if arquivo.size > FOTO_TAMANHO_MAXIMO:
        raise ValidationError('A foto deve ter no máximo 2 MB.')

    extensao = os.path.splitext(arquivo.name)[1].lower()
    if extensao not in FOTO_EXTENSOES:
        raise ValidationError('Formato não permitido. Envie uma foto JPG, PNG ou WEBP.')

    # Confere o conteúdo de verdade: um .txt renomeado para .jpg é barrado aqui.
    try:
        arquivo.seek(0)
        imagem = Image.open(arquivo)
        formato = imagem.format
        largura, altura = imagem.size
        imagem.verify()
    except Exception:
        # A biblioteca pode levantar vários tipos de erro com arquivo corrompido.
        raise ValidationError('O arquivo enviado não é uma imagem válida.')
    finally:
        arquivo.seek(0)   # devolve o ponteiro ao início para o arquivo poder ser salvo depois

    if formato not in FOTO_FORMATOS:
        raise ValidationError('Formato não permitido. Envie uma foto JPG, PNG ou WEBP.')
    if max(largura, altura) > FOTO_LADO_MAXIMO:
        raise ValidationError('A foto é grande demais (máximo 4000 pixels de largura ou altura).')


def caminho_foto_usuario(instance, nome_arquivo):
    """Nome aleatório: evita colisão e não aproveita o nome que o usuário mandou."""
    extensao = os.path.splitext(nome_arquivo)[1].lower()
    return f'usuarios/{uuid.uuid4().hex}{extensao}'


class TipoUsuario(models.Model):
    id_tipo_usuario = models.AutoField(primary_key=True)
    nome_tipo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nome_tipo or "Sem tipo definido"

class Endereco(models.Model):
    id_endereco = models.AutoField(primary_key=True)
    rua = models.CharField(max_length=100)
    numero_estabelecimento = models.CharField(max_length=10)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.rua}, {self.numero_estabelecimento}"


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    tipo_categoria = models.CharField(max_length=20)

    def __str__(self):
        return self.tipo_categoria

# 2. USUÁRIO E LOJA

class Usuario(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    cpf = models.CharField(max_length=11, unique=True, blank=True, null=True)
    id_tipo_usuario = models.ForeignKey(
        TipoUsuario, on_delete=models.CASCADE, db_column="id_tipo_usuario",
        blank=True, null=True
    )
    
    foto = models.ImageField(
        upload_to=caminho_foto_usuario,
        blank=True, null=True,
        validators=[validar_foto],
    )

    def __str__(self):
        return f"{self.nome} {self.sobrenome or ''}".strip()

class Loja(models.Model):
    id_loja = models.AutoField(primary_key=True)
    nome_loja = models.CharField(max_length=100)
    telefone_loja = models.CharField(max_length=15, blank=True, null=True)
    email_loja = models.EmailField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True) # !--!--!--!--!--!--!--! {{MUDAR PARA RECEBER TAMBEM CARACTERES "pois o CNPJ atual recebe letras tembem"}}  !--!--!--!--!--!--!--!
    foto_estabelecimento = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(max_length=255, blank=True, null=True)
    id_endereco = models.ForeignKey(
        Endereco, on_delete=models.CASCADE, db_column="id_endereco"
    )
    id_categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, db_column="id_categoria"
    )

    def __str__(self):
        return self.nome_loja


# 3. PRODUTO E SERVIÇO
class Produto(models.Model):
    id_produto = models.AutoField(primary_key=True)
    nome_produto = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True, null=True)
    foto = models.CharField(max_length=255, blank=True, null=True)
    id_loja = models.ForeignKey(
        Loja, on_delete=models.CASCADE, db_column="id_loja"
    )
    id_categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, db_column="id_categoria"
    )

    def __str__(self):
        return self.nome_produto


class Servico(models.Model):
    id_servico = models.AutoField(primary_key=True)
    nome_servico = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True, null=True)
    foto = models.CharField(max_length=255, blank=True, null=True)
    id_loja = models.ForeignKey(
        Loja, on_delete=models.CASCADE, db_column="id_loja"
    )

    def __str__(self):
        return self.nome_servico


# 4. TABELAS DE RELACIONAMENTO E AVALIAÇÃO
class LojaFavoritas(models.Model):
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column="id_usuario"
    )
    id_loja = models.ForeignKey(
        Loja, on_delete=models.CASCADE, db_column="id_loja"
    )

    class Meta:
        unique_together = (("id_usuario", "id_loja"),)

    def __str__(self):
        return f"{self.id_usuario.nome} - {self.id_loja.nome_loja}"


class Avaliacao(models.Model):
    nota = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column="id_usuario"
    )
    id_loja = models.ForeignKey(
        Loja, on_delete=models.CASCADE, db_column="id_loja", null=True, blank=True
    )
    id_produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, db_column="id_produto", null=True, blank=True
    )
    id_servico = models.ForeignKey(
        Servico, on_delete=models.CASCADE, db_column="id_servico", null=True, blank=True
    )

    def __str__(self):
        return f"Nota {self.nota} por {self.id_usuario.nome}"