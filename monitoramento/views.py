import random
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Sensor
from .mongo import collection


# ======================
# LOGIN / LOGOUT
# ======================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username") 
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "E-mail ou senha inválidos")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ======================
# DASHBOARD
# ======================

@login_required(login_url="/login/")
def dashboard(request):
    sensores = Sensor.objects.all()

    context = {
        "sensores": sensores,
        "sensores_ativos": sensores.filter(ativo=True).count(),
        "sensores_inativos": sensores.filter(ativo=False).count(),
    }

    return render(request, "monitoramento/dashboard.html", context)

# ======================
# SENSOR (SIMULAÇÃO)
# ======================

@login_required(login_url="/login/")
def simular_sensor(request):
    temperatura = round(random.uniform(18, 30), 2)
    umidade = round(random.uniform(40, 80), 2)
    gas_nh3 = round(random.uniform(0, 10), 2)

    # MySQL
    Sensor.objects.create(
        temperatura=temperatura,
        umidade=umidade,
        gas_nh3=gas_nh3
    )

    # MongoDB
    collection.insert_one({
        "temperatura": temperatura,
        "umidade": umidade,
        "gas_nh3": gas_nh3,
        "timestamp": datetime.now()
    })

    return redirect("dashboard")


# ======================
# OUTRAS TELAS
# ======================

@login_required(login_url="/login/")
def sensores(request):
    return render(request, "monitoramento/sensores.html")


@login_required(login_url="/login/")
def unidades(request):
    return render(request, "monitoramento/unidades.html")


@login_required(login_url="/login/")
def planta(request):
    return render(request, "monitoramento/planta.html")
