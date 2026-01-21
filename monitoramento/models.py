from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    # Adicionado default e blank=True para evitar erros de migração
    endereco = models.CharField(max_length=255, default="Não informado", blank=True)

    def __str__(self):
        return self.nome

class Unidade(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='unidades')

    def __str__(self):
        return f"{self.nome} ({self.empresa.nome})"

class Sensor(models.Model):
    nome = models.CharField(max_length=100)
    # Adicionado default para evitar o erro de 'non-nullable'
    tipo_sensor = models.CharField(max_length=50, default="Geral") 
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='sensores')
    ativo = models.BooleanField(default=True)
    data_instalacao = models.DateTimeField(auto_now_add=True)
    
    # Campos para Simulação
    temperatura = models.FloatField(null=True, blank=True, default=0.0)
    umidade = models.FloatField(null=True, blank=True, default=0.0)
    gas_nh3 = models.FloatField(null=True, blank=True, default=0.0)

    def __str__(self):
        return f"{self.nome} - {self.unidade.nome}"
    
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

