from django.db import models

# Create your models here.

class SensorData(models.Model):
    temperatura = models.FloatField()
    umidade = models.FloatField()
    gas_nh3 = models.FloatField()
    data_hora = models.DateTimeField(auto_now_add=True)

class Equipamento(models.Model):
    TIPO_CHOICES = [
        ("AC", "Ar-condicionado"),
        ("OUTRO", "Outro"),
    ]

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    local = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} - {self.local}"