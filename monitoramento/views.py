import random
from django.shortcuts import render
from .models import SensorData
from .mongo import collection
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "E-mail ou senha inválidos")

    return render(request, "auth/login.html")

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
def home(request):
    return render(request, "monitoramento/home.html")