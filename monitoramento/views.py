import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importação dos modelos e formulários
from .models import Sensor, Perfil, Unidade, Empresa
from .forms import EmpresaForm, UnidadeForm, SensorForm, UserForm
from .mongo import collection # Conexão com MongoDB

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
            messages.success(request, f"Bem-vindo, {username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Usuário ou senha inválidos")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ======================
# DASHBOARD
# ======================

@login_required(login_url="/login/")
def dashboard(request):
    try:
        perfil = Perfil.objects.get(user=request.user)
        empresa_do_usuario = perfil.empresa
    except Perfil.DoesNotExist:
        return render(request, "monitoramento/dashboard.html", {"error": "Usuário sem perfil vinculado"})

    # Busca sensores da empresa do usuário
    sensores_query = Sensor.objects.filter(unidade__empresa=empresa_do_usuario)

    context = {
        "sensores": sensores_query,
        "total_sensores": sensores_query.count(),
        "sensores_ativos": sensores_query.filter(ativo=True).count(),
        "sensores_inativos": sensores_query.filter(ativo=False).count(),
        "nome_empresa": empresa_do_usuario.nome
    }

    return render(request, "monitoramento/dashboard.html", context)


# ======================
# CADASTROS (VIEWS DE FORMULÁRIO)
# ======================

@login_required
def cadastro_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa cadastrada com sucesso!")
            return redirect('dashboard')
    else:
        form = EmpresaForm()
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Cadastro de Empresa'})

@login_required
def cadastro_unidade(request):
    if request.method == 'POST':
        form = UnidadeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Unidade/Filial cadastrada com sucesso!")
            return redirect('unidades')
    else:
        form = UnidadeForm()
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Cadastro de Filial'})

@login_required
def cadastro_sensor(request):
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipamento cadastrado com sucesso!")
            return redirect('sensores')
    else:
        form = SensorForm()
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Cadastro de Equipamento'})


# ======================
# SENSOR (SIMULAÇÃO)
# ======================

@login_required(login_url="/login/")
def simular_sensor(request):
    try:
        perfil = Perfil.objects.get(user=request.user)
        sensores = Sensor.objects.filter(unidade__empresa=perfil.empresa)

        if not sensores:
            messages.warning(request, "Cadastre um sensor primeiro para simular dados.")
            return redirect("sensores")

        for sensor in sensores:
            nova_temp = round(random.uniform(18, 30), 2)
            nova_umid = round(random.uniform(40, 80), 2)
            novo_gas = round(random.uniform(0, 10), 2)

            # --- Atualiza no MySQL ---
            sensor.temperatura = nova_temp
            sensor.umidade = nova_umid
            sensor.gas_nh3 = novo_gas
            sensor.save() 

            # --- Salva no MongoDB ---
            collection.insert_one({
                "sensor_id": sensor.id,
                "sensor_nome": sensor.nome,
                "unidade": sensor.unidade.nome,
                "temperatura": nova_temp,
                "umidade": nova_umid,
                "gas_nh3": novo_gas,
                "timestamp": datetime.now()
            })
        
        messages.success(request, "Simulação concluída! Dados atualizados.")

    except Exception as e:
        messages.error(request, f"Erro na simulação: {e}")

    return redirect("dashboard")


# ======================
# LISTAGENS (TELAS DA NAVBAR)
# ======================

@login_required(login_url="/login/")
def sensores(request):
    perfil = Perfil.objects.get(user=request.user)
    # Busca sensores reais do banco
    lista_sensores = Sensor.objects.filter(unidade__empresa=perfil.empresa)
    
    # Busca os últimos 10 registros do MongoDB para o histórico
    try:
        historico_logs = list(collection.find().sort("timestamp", -1).limit(10))
    except:
        historico_logs = []

    return render(request, "monitoramento/sensores.html", {
        "sensores": lista_sensores,
        "logs": historico_logs
    })


@login_required(login_url="/login/")
def unidades(request):
    perfil = Perfil.objects.get(user=request.user)
    # Lista todas as unidades daquela empresa
    lista_unidades = Unidade.objects.filter(empresa=perfil.empresa)
    
    return render(request, "monitoramento/unidades.html", {
        "unidades": lista_unidades
    })


@login_required(login_url="/login/")
def planta(request):
    # Por enquanto apenas renderiza, no futuro você pode passar as coordenadas dos sensores aqui
    return render(request, "monitoramento/planta.html")