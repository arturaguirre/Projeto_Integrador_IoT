from django import forms
from django.contrib.auth.models import User
from .models import Empresa, Unidade, Sensor, Perfil

# Atributos de estilo para todos os campos (Tema Dark)
css_attrs = {'class': 'form-control bg-dark text-white border-secondary'}

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'cnpj', 'email', 'telefone', 'endereco', 'logo']
        widgets = {
            'nome': forms.TextInput(attrs=css_attrs),
            'cnpj': forms.TextInput(attrs=css_attrs),
            'email': forms.EmailInput(attrs=css_attrs),
            'telefone': forms.TextInput(attrs=css_attrs),
            'endereco': forms.TextInput(attrs=css_attrs),
        }

class UnidadeForm(forms.ModelForm):
    class Meta:
        model = Unidade
        fields = ['nome', 'cidade', 'estado', 'empresa']
        widgets = {
            'nome': forms.TextInput(attrs=css_attrs),
            'cidade': forms.TextInput(attrs=css_attrs),
            'estado': forms.TextInput(attrs=css_attrs),
            'empresa': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        }
    def __init__(self, *args, **kwargs):
        # Capturamos o usuário logado passado pela view
        user_empresa = kwargs.pop('empresa', None)
        super(UnidadeForm, self).__init__(*args, **kwargs)
        if user_empresa:
            # Forçamos o campo empresa a mostrar apenas a empresa do usuário
            self.fields['empresa'].queryset = Empresa.objects.filter(id=user_empresa.id)
            self.fields['empresa'].initial = user_empresa

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['nome', 'tipo_sensor', 'unidade', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs=css_attrs),
            'tipo_sensor': forms.TextInput(attrs=css_attrs),
            'unidade': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        user_empresa = kwargs.pop('empresa', None)
        super(SensorForm, self).__init__(*args, **kwargs)
        if user_empresa:
            # O sensor só pode ser vinculado a uma unidade da empresa do usuário
            self.fields['unidade'].queryset = Unidade.objects.filter(empresa=user_empresa)

class RegistroUsuarioForm(forms.ModelForm):
    # Campos do User padrão
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}), label="Nome de Usuário")
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}), label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}), label="Senha")
    
    # Campo do Perfil
    cargo = forms.ChoiceField(
        choices=Perfil.CARGOS, 
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        label="Cargo / Nível de Acesso"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']