from django.contrib import admin
from .models import Empresa, Unidade, Sensor, Perfil


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "email", "telefone", "data_criacao")
    search_fields = ("nome", "cnpj")


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "empresa", "cidade", "estado")
    list_filter = ("estado", "empresa")
    search_fields = ("nome",)


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "unidade", "ativo")
    list_filter = ("tipo", "ativo")
    search_fields = ("nome",)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "empresa", "cargo")
    list_filter = ("cargo", "empresa")
