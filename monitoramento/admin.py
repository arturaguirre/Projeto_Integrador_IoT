from django.contrib import admin
from .models import SensorData, Equipamento


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('temperatura', 'umidade', 'gas_nh3', 'data_hora')


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'local')
