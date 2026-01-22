from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboards e Listagens
    path("", views.dashboard, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("sensores/", views.sensores, name="sensores"),
    path("unidades/", views.unidades, name="unidades"),
    path("planta/", views.planta, name="planta"),
    
    # Operações de Dados
    path('simular-sensor/', views.simular_sensor, name='simular_sensor'),

    # Administrativo - Gestão de Equipe
    path('administrativo/equipe/', views.gerenciar_equipe, name='gerenciar_equipe'),
    path('administrativo/equipe/excluir/<int:user_id>/', views.excluir_usuario, name='excluir_usuario'),
    path('administrativo/empresas/editar/<int:empresa_id>/', views.editar_empresa, name='editar_empresa'),
    path('administrativo/empresas/', views.listar_empresas, name='listar_empresas'),
    path('administrativo/empresas/excluir/<int:empresa_id>/', views.excluir_empresa, name='excluir_empresa'),

    # Cadastros
    path('cadastro/empresa/', views.cadastro_empresa, name='cadastro_empresa'),
    path('cadastro/unidade/', views.cadastro_unidade, name='cadastro_unidade'),
    path('cadastro/sensor/', views.cadastro_sensor, name='cadastro_sensor'),
    
    # Cadastro de Usuário (Duas rotas para o mesmo formulário)
    # 1. Cadastro normal via painel de equipe
    path('cadastro/usuario/', views.cadastro_usuario, name='cadastro_usuario'),
    # 2. Cadastro vinculado à nova empresa (Fluxo de criação de conta)
    path('cadastro/usuario/<int:empresa_id>/', views.cadastro_usuario, name='cadastro_usuario_empresa'),
]