from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
class Unidade(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="unidades")
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome} - {self.empresa.nome}"
    
class Sensor(models.Model):
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name="sensores")
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)  # ex: Temperatura, Gás, Umidade
    ativo = models.BooleanField(default=True)
    data_instalacao = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.unidade.nome})"
    
class Perfil(models.Model):
    CARGOS = (
        ("ADMIN", "Administrador"),
        ("TECNICO", "Técnico"),
        ("OPERADOR", "Operador"),
        ("VISUALIZADOR", "Visualizador"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=20, choices=CARGOS)

    def __str__(self):
        return f"{self.user.username} - {self.cargo}"

