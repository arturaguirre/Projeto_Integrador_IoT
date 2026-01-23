from django.urls import path
from . import views

urlpatterns = [
    # --- Autenticação ---
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # --- Dashboards e Visões Principais ---
    path("", views.dashboard, name="home"), 
    path("dashboard/", views.dashboard, name="dashboard"),
    path("sensores/", views.sensores, name="sensores"),
    path("unidades/", views.unidades, name="unidades"),
    path("planta/", views.planta, name="planta"),
    
    # --- Operações de Dados e Simulação ---
    path('simular-sensor/', views.simular_sensor, name='simular_sensor'),

    # --- Gestão de Empresas (Exclusivo Superuser) ---
    path('administrativo/empresas/', views.listar_empresas, name='listar_empresas'),
    path('administrativo/empresas/editar/<int:empresa_id>/', views.editar_empresa, name='editar_empresa'),
    path('administrativo/empresas/excluir/<int:empresa_id>/', views.excluir_empresa, name='excluir_empresa'),

    # --- Gestão de Equipe (Usuários Internos) ---
    path('administrativo/equipe/', views.gerenciar_equipe, name='gerenciar_equipe'),
    path('administrativo/equipe/excluir/<int:user_id>/', views.excluir_usuario, name='excluir_usuario'),

    # --- Fluxo de Cadastros de Objetos ---
    path('cadastro/empresa/', views.cadastro_empresa, name='cadastro_empresa'),
    path('cadastro/unidade/', views.cadastro_unidade, name='cadastro_unidade'),
    path('cadastro/sensor/', views.cadastro_sensor, name='cadastro_sensor'),
    
    # --- Fluxo de Cadastro de Usuários ---
    path('cadastro/usuario/', views.cadastro_usuario, name='cadastro_usuario'),
    path('cadastro/usuario/<int:empresa_id>/', views.cadastro_usuario, name='cadastro_usuario_empresa'),
    path("registro/", views.registro_externo, name="registro"),
]