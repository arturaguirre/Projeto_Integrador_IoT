from django.db import models

# Create your models here.

class SensorData(models.Model):
    temperatura = models.FloatField()
    umidade = models.FloatField()
    gas_nh3 = models.FloatField()
    data_hora = models.DateTimeField(auto_now_add=True)