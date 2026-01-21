from django.contrib import admin
from .models import Empresa, Unidade, Sensor, Perfil

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    # Removido 'data_criacao' que não existe no modelo
    list_display = ('nome', 'cnpj', 'email', 'telefone', 'endereco')
    search_fields = ('nome', 'cnpj')

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado', 'empresa')
    list_filter = ('estado', 'empresa')
    search_fields = ('nome', 'cidade')

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    # Alterado de 'tipo' para 'tipo_sensor' para bater com o models.py
    list_display = ('nome', 'tipo_sensor', 'unidade', 'ativo', 'temperatura', 'umidade')
    list_filter = ('tipo_sensor', 'ativo', 'unidade')
    search_fields = ('nome',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "empresa", "cargo")
    list_filter = ("cargo", "empresa")
