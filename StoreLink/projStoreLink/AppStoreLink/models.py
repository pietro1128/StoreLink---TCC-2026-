from django.db import models
# Create your models here.

class TipoUsuario(models.Model):
    id_tipo_usuario = models.AutoField(primary_key=True)
    nome_tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.nome_tipo

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    cpf = models.CharField(max_length=11, unique=True)
    id_tipo_usuario = models.ForeignKey(
        TipoUsuario, on_delete=models.CASCADE, db_column="id_tipo_usuario"
    )

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"


# 1. TABELAS DE SUPORTE (Criadas primeiro para servirem de Foreign Key)
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


class TipoUsuario(models.Model):
    id_tipo_usuario = models.AutoField(primary_key=True)
    tipo_usuario = models.CharField(max_length=12)

    def __str__(self):
        return self.tipo_usuario


# 2. USUÁRIO E LOJA
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    cpf = models.CharField(max_length=11, unique=True)
    id_tipo_usuario = models.ForeignKey(
        TipoUsuario, on_delete=models.CASCADE, db_column="id_tipo_usuario"
    )

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"


class Loja(models.Model):
    id_loja = models.AutoField(primary_key=True)
    nome_loja = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    telefone_loja = models.CharField(max_length=15, blank=True, null=True)
    email_loja = models.EmailField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
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