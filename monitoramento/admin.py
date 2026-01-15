from django.contrib import admin
from .models import SensorData

# Register your models here.

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('temperatura', 'umidade', 'gas_nh3', 'data_hora')