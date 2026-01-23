from django.contrib import admin
from .models import Empresa, Unidade, Sensor, Perfil

# Melhora o título do cabeçalho do Admin
admin.site.site_header = "Boreas IoT | Painel Administrativo"
admin.site.site_title = "Boreas IoT Admin"
admin.site.index_title = "Gerenciamento de Infraestrutura e Sensores"

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'telefone', 'endereco')
    search_fields = ('nome', 'cnpj', 'email')
    list_per_page = 20

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado', 'empresa')
    list_filter = ('estado', 'empresa')
    search_fields = ('nome', 'cidade')
    autocomplete_fields = ['empresa'] # Facilita a busca se houver muitas empresas

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_sensor', 'unidade', 'get_empresa', 'ativo', 'temperatura', 'umidade')
    list_filter = ('tipo_sensor', 'ativo', 'unidade', 'unidade__empresa')
    search_fields = ('nome',)
    # Impede que alguém mude a temperatura/umidade manualmente pelo admin (deve vir do sensor)
    readonly_fields = ('temperatura', 'umidade')
    
    # Função para mostrar a empresa dona do sensor na lista
    def get_empresa(self, obj):
        return obj.unidade.empresa
    get_empresa.short_description = 'Empresa'
    get_empresa.admin_order_field = 'unidade__empresa'

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "empresa", "cargo")
    list_filter = ("cargo", "empresa")
    search_fields = ("user__username", "user__email", "empresa__nome")
    
    # Organiza os campos no formulário de edição
    fieldsets = (
        (None, {
            'fields': ('user', 'empresa', 'cargo')
        }),
    )