import random
from django.shortcuts import render
from .models import SensorData
from .mongo import collection
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import redirect

def simular_sensor(request):
    temperatura = round(random.uniform(18, 30), 2)
    umidade = round(random.uniform(40, 80), 2)
    gas_nh3 = round(random.uniform(0, 10), 2)

    # Salva no MySQL
    SensorData.objects.create(
        temperatura=temperatura,
        umidade=umidade,
        gas_nh3=gas_nh3
    )

    # Salva no MongoDB
    collection.insert_one({
        "temperatura": temperatura,
        "umidade": umidade,
        "gas_nh3": gas_nh3,
        "timestamp": datetime.now()
    })
    
    return redirect("dashboard")



def dashboard(request):
    dados = SensorData.objects.all().order_by("-id")[:20]

    return render(request, "monitoramento/dashboard.html", {
        "dados": dados
    })