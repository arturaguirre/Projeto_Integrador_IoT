from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("", views.dashboard, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("sensores/", views.sensores, name="sensores"),
    path("unidades/", views.unidades, name="unidades"),
    path("planta/", views.planta, name="planta"),
    path('simular-sensor/', views.simular_sensor, name='simular_sensor'),

    path('cadastro/empresa/', views.cadastro_empresa, name='cadastro_empresa'),
    path('cadastro/unidade/', views.cadastro_unidade, name='cadastro_unidade'),
    path('cadastro/sensor/', views.cadastro_sensor, name='cadastro_sensor'),
]
