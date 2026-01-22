import random
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

# Importação dos modelos e formulários
from .forms import EmpresaForm, UnidadeForm, SensorForm, RegistroUsuarioForm
from .models import Sensor, Perfil, Unidade, Empresa
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
            messages.success(request, f"Bem-vindo, {username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Usuário ou senha inválidos")

    return render(request, "auth/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# ======================
# DASHBOARD (CORRIGIDO)
# ======================

@login_required(login_url="/login/")
def dashboard(request):
    try:
        perfil = Perfil.objects.get(user=request.user)
        empresa_do_usuario = perfil.empresa
        
        sensores_query = Sensor.objects.filter(unidade__empresa=empresa_do_usuario)

        context = {
            "sensores": sensores_query,
            "total_sensores": sensores_query.count(),
            "sensores_ativos": sensores_query.filter(ativo=True).count(),
            "sensores_inativos": sensores_query.filter(ativo=False).count(),
            "nome_empresa": empresa_do_usuario.nome
        }
        return render(request, "monitoramento/dashboard.html", context)

    except Perfil.DoesNotExist:
        # Se for Superuser sem perfil, redireciona para a gestão geral em vez de travar
        if request.user.is_superuser:
            return redirect('listar_empresas')
        
        # Se for usuário comum sem perfil, desconecta por segurança
        logout(request)
        messages.error(request, "Seu usuário não possui um perfil vinculado.")
        return redirect('login')

# ======================
# GESTÃO DE EQUIPE
# ======================

@login_required
def gerenciar_equipe(request):
    try:
        perfil_gestor = request.user.perfil
        if perfil_gestor.cargo != 'gestor' and not request.user.is_superuser:
            messages.error(request, "Acesso restrito a Gestores.")
            return redirect('dashboard')
        
        equipe = Perfil.objects.filter(empresa=perfil_gestor.empresa).select_related('user')
        
        return render(request, 'monitoramento/equipe.html', {
            'equipe': equipe,
            'unidade_nome': perfil_gestor.empresa.nome
        })
    except Perfil.DoesNotExist:
        if request.user.is_superuser:
             messages.warning(request, "Admin, você não possui uma empresa vinculada.")
             return redirect('listar_empresas')
        return redirect('login')

@login_required
def excluir_usuario(request, user_id):
    perfil_gestor = get_object_or_404(Perfil, user=request.user)
    perfil_alvo = get_object_or_404(Perfil, user_id=user_id)

    if (perfil_gestor.cargo == 'gestor' and perfil_gestor.empresa == perfil_alvo.empresa) or request.user.is_superuser:
        user_alvo = perfil_alvo.user
        if user_alvo == request.user:
            messages.error(request, "Você não pode excluir seu próprio usuário.")
        else:
            user_alvo.delete()
            messages.success(request, "Usuário removido com sucesso.")
    else:
        messages.error(request, "Permissão negada.")
    
    return redirect('gerenciar_equipe')

# ======================
# GESTÃO DE EMPRESAS (MATRIZES)
# ======================

@login_required
def listar_empresas(request):
    # Superuser vê todas, Gestor vê apenas a sua
    if request.user.is_superuser:
        empresas = Empresa.objects.all()
    else:
        try:
            perfil = request.user.perfil
            if perfil.cargo == 'gestor':
                empresas = Empresa.objects.filter(id=perfil.empresa.id)
            else:
                messages.error(request, "Acesso negado.")
                return redirect('dashboard')
        except Perfil.DoesNotExist:
            return redirect('login')
            
    return render(request, 'monitoramento/empresas_lista.html', {'empresas': empresas})

@login_required
def cadastro_empresa(request):
    # Apenas superuser ou gestores podem criar empresas
    cargo = getattr(getattr(request.user, 'perfil', None), 'cargo', None)
    if not (request.user.is_superuser or cargo == 'gestor'):
        messages.error(request, "Acesso negado.")
        return redirect('dashboard')

    if request.method == 'POST':
        # request.FILES adicionado para suportar o upload da LOGO
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            nova_empresa = form.save()
            messages.success(request, f"Empresa '{nova_empresa.nome}' criada! Prossiga com o cadastro do gestor.")
            return redirect('cadastro_usuario_empresa', empresa_id=nova_empresa.id)
    else:
        form = EmpresaForm()
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Nova Matriz'})

@login_required
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    # Trava: Gestor só edita a própria empresa, Superuser edita qualquer uma
    if not request.user.is_superuser:
        if request.user.perfil.empresa != empresa:
            messages.error(request, "Você não tem permissão para editar esta empresa.")
            return redirect('dashboard')

    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, f"Empresa {empresa.nome} atualizada!")
            return redirect('listar_empresas')
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'monitoramento/form_cadastro.html', {
        'form': form, 
        'titulo': f"Editando: {empresa.nome}"
    })

@login_required
def excluir_empresa(request, empresa_id):
    if not request.user.is_superuser:
        messages.error(request, "Apenas administradores do sistema podem excluir empresas.")
        return redirect('dashboard')
        
    empresa = get_object_or_404(Empresa, id=empresa_id)
    empresa.delete()
    messages.warning(request, f"Empresa {empresa.nome} removida.")
    return redirect('listar_empresas')

# ======================
# CADASTRO DE USUÁRIOS
# ======================

@login_required
def cadastro_usuario(request, empresa_id=None):
    empresa_alvo = None
    
    if empresa_id:
        empresa_alvo = get_object_or_404(Empresa, id=empresa_id)
    else:
        try:
            perfil_logado = request.user.perfil
            if perfil_logado.cargo != 'gestor' and not request.user.is_superuser:
                messages.error(request, "Sem permissão para cadastrar usuários.")
                return redirect('dashboard')
            empresa_alvo = perfil_logado.empresa
        except Perfil.DoesNotExist:
            return redirect('listar_empresas')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            Perfil.objects.create(
                user=user, 
                empresa=empresa_alvo,
                cargo=form.cleaned_data['cargo']
            )
            
            messages.success(request, f"Usuário {user.username} cadastrado em {empresa_alvo.nome}!")
            return redirect('listar_empresas') if empresa_id else redirect('gerenciar_equipe')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'monitoramento/form_cadastro.html', {
        'form': form, 
        'titulo': f"Novo Usuário para {empresa_alvo.nome}"
    })

# ======================
# UNIDADES E SENSORES
# ======================

@login_required
def cadastro_unidade(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    if request.method == 'POST':
        form = UnidadeForm(request.POST, empresa=perfil.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Unidade cadastrada!")
            return redirect('unidades')
    else:
        form = UnidadeForm(empresa=perfil.empresa)
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Nova Unidade'})

@login_required
def cadastro_sensor(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    if request.method == 'POST':
        form = SensorForm(request.POST, empresa=perfil.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipamento registrado!")
            return redirect('sensores')
    else:
        form = SensorForm(empresa=perfil.empresa)
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Novo Sensor'})

@login_required
def simular_sensor(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    sensores = Sensor.objects.filter(unidade__empresa=perfil.empresa)

    if not sensores.exists():
        messages.warning(request, "Cadastre um sensor primeiro.")
        return redirect("sensores")

    for sensor in sensores:
        nova_temp = round(random.uniform(18, 30), 2)
        nova_umid = round(random.uniform(40, 80), 2)
        novo_gas = round(random.uniform(0, 10), 2)

        sensor.temperatura = nova_temp
        sensor.umidade = nova_umid
        sensor.gas_nh3 = novo_gas
        sensor.save() 

        collection.insert_one({
            "sensor_id": sensor.id,
            "sensor_nome": sensor.nome,
            "unidade": sensor.unidade.nome,
            "temperatura": nova_temp,
            "umidade": nova_umid,
            "gas_nh3": novo_gas,
            "timestamp": datetime.now()
        })
    messages.success(request, "Simulação concluída!")
    return redirect("dashboard")

@login_required
def sensores(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    lista_sensores = Sensor.objects.filter(unidade__empresa=perfil.empresa)
    try:
        historico_logs = list(collection.find().sort("timestamp", -1).limit(10))
    except:
        historico_logs = []
    return render(request, "monitoramento/sensores.html", {"sensores": lista_sensores, "logs": historico_logs})

@login_required
def unidades(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    lista_unidades = Unidade.objects.filter(empresa=perfil.empresa)
    return render(request, "monitoramento/unidades.html", {"unidades": lista_unidades})

@login_required
def planta(request):
    return render(request, "monitoramento/planta.html")