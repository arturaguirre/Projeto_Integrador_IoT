from  django.urls import path
from .views import home, simular_sensor,dashboard,login_view

urlpatterns = [ 
    path("", home, name="home"),
    path("simular/", simular_sensor, name= "simular"),
    path("dashboard/", dashboard, name= "dashboard"),
    path("", login_view, name="login"),
]