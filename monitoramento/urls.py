from  django.urls import path
from .views import simular_sensor,dashboard

urlpatterns = [ 
    path("simular/", simular_sensor, name= "simular"),
    path("dashboard/", dashboard, name= "dashboard"),
]