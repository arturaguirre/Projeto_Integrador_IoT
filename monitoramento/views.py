import random
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction

from .forms import EmpresaForm, UnidadeForm, SensorForm, RegistroUsuarioForm
from .models import Sensor, Perfil, Unidade, Empresa
from .mongo import collection

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if not hasattr(user, 'perfil') and not user.is_superuser:
                messages.warning(request, "Atenção: Seu usuário não possui perfil vinculado.")
            return redirect("home")
        else:
            messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required(login_url="/login/")
def dashboard(request):
    sensores_query = Sensor.objects.none()
    nome_empresa = "Não identificado"
    mostrar_tutorial = False
    if request.user.is_superuser:
        sensores_query = Sensor.objects.all()
        nome_empresa = "Administração Global (Superuser)"
    else:
        try:
            perfil = request.user.perfil
            empresa_do_usuario = perfil.empresa
            sensores_query = Sensor.objects.filter(unidade__empresa=empresa_do_usuario)
            nome_empresa = empresa_do_usuario.nome
            if 'gestor' in perfil.cargo.lower():
                if not Unidade.objects.filter(empresa=empresa_do_usuario).exists():
                    mostrar_tutorial = True

        except Perfil.DoesNotExist:
            messages.error(request, "Seu usuário não possui um perfil vinculado.")

    logs_recentes = []
    if collection is not None and sensores_query.exists():
        ids_sensores = list(sensores_query.values_list('id', flat=True))
        try:
            logs_recentes = list(collection.find(
                {"sensor_id": {"$in": ids_sensores}}
            ).sort("timestamp", -1).limit(10))
        except Exception as e:
            print(f"Erro ao ler Mongo: {e}")

    context = {
        "sensores": sensores_query,
        "total_sensores": sensores_query.count(),
        "sensores_ativos": sensores_query.filter(ativo=True).count(),
        "sensores_inativos": sensores_query.filter(ativo=False).count(),
        "nome_empresa": nome_empresa,
        "logs": logs_recentes,
        "mostrar_tutorial": mostrar_tutorial
    }
    return render(request, "monitoramento/dashboard.html", context)

@login_required
def gerenciar_equipe(request):
    if request.user.is_superuser:
        equipe = Perfil.objects.all().select_related('user', 'empresa')
        unidade_nome = "Todas as Unidades (Admin Global)"
    else:
        try:
            perfil_user = request.user.perfil
            if 'gestor' in perfil_user.cargo.lower():
                equipe = Perfil.objects.filter(empresa=perfil_user.empresa).select_related('user')
                unidade_nome = perfil_user.empresa.nome
            else:
                messages.error(request, "Acesso restrito a Gestores.")
                return redirect('home')
        except Perfil.DoesNotExist:
            return redirect('home')

    return render(request, 'monitoramento/equipe.html', {
        'equipe': equipe,
        'unidade_nome': unidade_nome
    })


@login_required
def excluir_usuario(request, user_id):
    user_alvo = get_object_or_404(User, id=user_id)

    if user_alvo == request.user:
        messages.error(request, "Você não pode excluir sua própria conta.")
        return redirect('gerenciar_equipe')

    if request.user.is_superuser:
        user_alvo.delete()
        messages.success(request, "Usuário removido pelo Admin.")
    else:
        try:
            perfil_gestor = request.user.perfil
            perfil_alvo = user_alvo.perfil

            if 'gestor' in perfil_gestor.cargo.lower() and perfil_gestor.empresa == perfil_alvo.empresa:
                user_alvo.delete()
                messages.success(request, "Colaborador removido da empresa.")
            else:
                messages.error(request, "Permissão negada.")
        except:
            messages.error(request, "Erro ao processar exclusão.")

    return redirect('gerenciar_equipe')

@login_required
def listar_empresas(request):
    if request.user.is_superuser:
        empresas = Empresa.objects.all()
    else:
        try:
            perfil = request.user.perfil
            if 'gestor' in perfil.cargo.lower():
                # Gestor só vê a sua própria empresa (isolamento por perfil)
                empresas = Empresa.objects.filter(id=perfil.empresa.id)
            else:
                messages.error(request, "Acesso restrito.")
                return redirect('home')
        except Perfil.DoesNotExist:
            return redirect('home')

    return render(request, 'monitoramento/empresa_lista.html', {'empresas': empresas})


@login_required
def cadastro_empresa(request):
    tem_permissao = False

    if request.user.is_superuser:
        tem_permissao = True
    else:
        try:
            perfil = request.user.perfil
            if 'gestor' in perfil.cargo.lower():
                tem_permissao = True
        except Perfil.DoesNotExist:
            pass

    if not tem_permissao:
        messages.error(request, "Apenas gestores e administradores podem cadastrar novas empresas.")
        return redirect('home')

    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            nova_empresa = form.save()
            messages.success(request, f"Empresa '{nova_empresa.nome}' criada!")
            return redirect('listar_empresas')
    else:
        form = EmpresaForm()
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Nova Empresa Matriz'})


@login_required
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    permissao = False
    if request.user.is_superuser:
        permissao = True
    else:
        try:
            perfil = request.user.perfil
            if 'gestor' in perfil.cargo.lower() and perfil.empresa == empresa:
                permissao = True
        except Perfil.DoesNotExist:
            pass

    if not permissao:
        messages.error(request, "Você não tem permissão para editar esta empresa.")
        return redirect('home')

    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados da empresa atualizados!")
            return redirect('listar_empresas')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': f"Editar: {empresa.nome}"})


@login_required
def excluir_empresa(request, empresa_id):
    if not request.user.is_superuser:
        messages.error(request, "Apenas administradores globais podem excluir empresas.")
        return redirect('home')

    empresa = get_object_or_404(Empresa, id=empresa_id)
    empresa.delete()
    messages.warning(request, "Empresa e seus dados foram removidos.")
    return redirect('listar_empresas')

@login_required
def unidades(request):
    if request.user.is_superuser:
        lista_unidades = Unidade.objects.all()
    else:
        try:
            perfil = request.user.perfil
            lista_unidades = Unidade.objects.filter(empresa=perfil.empresa)
        except Perfil.DoesNotExist:
            return redirect('home')
    return render(request, "monitoramento/unidades.html", {"unidades": lista_unidades})


@login_required
def cadastro_unidade(request):
    empresa_usuario = None
    if not request.user.is_superuser:
        try:
            empresa_usuario = request.user.perfil.empresa
        except:
            return redirect('home')

    if request.method == 'POST':
        form = UnidadeForm(request.POST, empresa=empresa_usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Unidade cadastrada com sucesso!")
            return redirect('unidades')
    else:
        form = UnidadeForm(empresa=empresa_usuario)

    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Nova Unidade Operacional'})


@login_required
def sensores(request):
    if request.user.is_superuser:
        lista_sensores = Sensor.objects.all()
    else:
        try:
            perfil = request.user.perfil
            lista_sensores = Sensor.objects.filter(unidade__empresa=perfil.empresa)
        except Perfil.DoesNotExist:
            return redirect('home')

    unidade_id = request.GET.get('unidade')
    if unidade_id:
        lista_sensores = lista_sensores.filter(unidade_id=unidade_id)

    logs_sensores = []
    if collection is not None and lista_sensores.exists():
        ids = list(lista_sensores.values_list('id', flat=True))
        try:
            logs_sensores = list(collection.find({"sensor_id": {"$in": ids}}).sort("timestamp", -1).limit(20))
        except:
            pass

    return render(request, "monitoramento/sensores.html", {
        "sensores": lista_sensores,
        "logs": logs_sensores
    })


@login_required
def cadastro_sensor(request):
    empresa_usuario = None
    if not request.user.is_superuser:
        try:
            empresa_usuario = request.user.perfil.empresa
        except:
            return redirect('home')

    if request.method == 'POST':
        form = SensorForm(request.POST, empresa=empresa_usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Novo sensor conectado ao sistema!")
            return redirect('sensores')
    else:
        form = SensorForm(empresa=empresa_usuario)
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': 'Cadastrar Sensor IoT'})

@login_required
def simular_sensor(request):
    if request.user.is_superuser:
        sensores_lista = Sensor.objects.filter(ativo=True)
    else:
        try:
            sensores_lista = Sensor.objects.filter(unidade__empresa=request.user.perfil.empresa, ativo=True)
        except:
            return redirect('home')

    if not sensores_lista.exists():
        messages.warning(request, "Nenhum sensor ativo encontrado para simular.")
        return redirect("sensores")

    count_leituras = 0
    for s in sensores_lista:
        t = round(random.uniform(20.0, 35.0), 1)
        u = round(random.uniform(40.0, 80.0), 1)
        g = round(random.uniform(0.0, 5.0), 2)

        s.temperatura = t
        s.umidade = u
        s.gas_nh3 = g
        s.save()

        if collection is not None:
            try:
                documento = {
                    "sensor_id": s.id,
                    "sensor_nome": s.nome,
                    "unidade_id": s.unidade.id,
                    "unidade_nome": s.unidade.nome,
                    "temperatura": t,
                    "umidade": u,
                    "gas_nh3": g,
                    "timestamp": datetime.now()
                }
                collection.insert_one(documento)
                count_leituras += 1
            except Exception as e:
                print(f"Erro ao salvar no Mongo: {e}")

    messages.success(request, f"Simulação concluída! {count_leituras} novas leituras geradas.")
    return redirect("sensores")


@login_required
def planta(request):
    unidade_id = request.GET.get('unidade')
    unidade_nome = "Matriz Principal"

    query_unidade = Unidade.objects.all()
    if not request.user.is_superuser:
        try:
            query_unidade = query_unidade.filter(empresa=request.user.perfil.empresa)
        except:
            return redirect('home')

    if unit_obj := query_unidade.filter(id=unidade_id).first():
        unidade_nome = unit_obj.nome
    else:
        if primeira := query_unidade.first():
            unidade_nome = primeira.nome

    return render(request, "monitoramento/planta.html", {'unidade_nome': unidade_nome})

@login_required
def cadastro_usuario(request, empresa_id=None):
    empresa_alvo = None

    if request.user.is_superuser:
        if empresa_id:
            empresa_alvo = get_object_or_404(Empresa, id=empresa_id)
    else:
        try:
            perfil_logado = request.user.perfil
            if 'gestor' not in perfil_logado.cargo.lower():
                messages.error(request, "Acesso negado.")
                return redirect('home')
            empresa_alvo = perfil_logado.empresa
        except Perfil.DoesNotExist:
            return redirect('home')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, empresa=empresa_alvo)
        if form.is_valid():
            user_criado = form.save()
            empresa_final = form.cleaned_data.get('empresa') or empresa_alvo

            Perfil.objects.create(
                user=user_criado,
                empresa=empresa_final,
                cargo=form.cleaned_data['cargo']
            )

            messages.success(request, f"Usuário {user_criado.username} cadastrado!")
            return redirect('gerenciar_equipe')
    else:
        form = RegistroUsuarioForm(empresa=empresa_alvo)

    titulo = f"Novo Usuário - {empresa_alvo.nome}" if empresa_alvo else "Novo Usuário (Admin)"
    return render(request, 'monitoramento/form_cadastro.html', {'form': form, 'titulo': titulo})

def registro_externo(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa')
        cnpj = request.POST.get('cnpj')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "As senhas não conferem.")
            return render(request, 'auth/registro.html')

        try:
            with transaction.atomic():
                nova_empresa = Empresa.objects.create(nome=nome_empresa, cnpj=cnpj)
                novo_usuario = User.objects.create_user(username=username, email=email, password=password)
                Perfil.objects.create(
                    user=novo_usuario,
                    empresa=nova_empresa,
                    cargo="Gestor"
                )

                login(request, novo_usuario)
                messages.success(request, f"Bem-vindo! Sua empresa {nome_empresa} foi registrada.")
                return redirect('home')
        except Exception as e:
            messages.error(request, f"Erro ao registrar: {e}")

    return render(request, 'auth/registro.html')