from django.db import models
from django.contrib.auth.models import User
import os

class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, default="Não informado", blank=True)
    logo = models.ImageField(upload_to='empresa_logos/', null=True, blank=True)

    def __str__(self):
        return self.nome

    def delete(self, *args, **kwargs):
        if self.logo:
            if os.path.isfile(self.logo.path):
                os.remove(self.logo.path)
        super().delete(*args, **kwargs)

class Unidade(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='unidades')

    def __str__(self):
        return f"{self.nome} ({self.empresa.nome})"

class Sensor(models.Model):
    nome = models.CharField(max_length=100)
    tipo_sensor = models.CharField(max_length=50, default="Geral") 
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='sensores')
    ativo = models.BooleanField(default=True)
    data_instalacao = models.DateTimeField(auto_now_add=True)
    temperatura = models.FloatField(null=True, blank=True, default=0.0)
    umidade = models.FloatField(null=True, blank=True, default=0.0)
    gas_nh3 = models.FloatField(null=True, blank=True, default=0.0)

    def __str__(self):
        return f"{self.nome} - {self.unidade.nome}"
    
    class Meta:
        verbose_name_plural = "Sensores"

class Perfil(models.Model):
    CARGOS = [
        ("gestor", "Gestor (Administrador - Full Access)"),
        ("tecnico", "Técnico (Manutenção/Sensores)"),
        ("operador", "Operador (Visualização/Uso Geral)"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='colaboradores')
    
    # Opcional: Vincular o usuário a uma unidade específica (ex: Operador de um galpão só)
    unidade = models.ForeignKey(Unidade, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=20, choices=CARGOS, default="operador")

    def __str__(self):
        return f"{self.user.username} - {self.get_cargo_display()} ({self.empresa.nome})"
    
    class Meta:
        verbose_name_plural = "Perfis"