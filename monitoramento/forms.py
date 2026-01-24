from django import forms
from django.contrib.auth.models import User
from .models import Empresa, Unidade, Sensor, Perfil
css_attrs = {'class': 'form-control bg-dark text-white border-secondary'}
select_attrs = {'class': 'form-select bg-dark text-white border-secondary'}

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
            'logo': forms.FileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }

class UnidadeForm(forms.ModelForm):
    class Meta:
        model = Unidade
        fields = ['nome', 'cidade', 'estado', 'empresa']
        widgets = {
            'nome': forms.TextInput(attrs=css_attrs),
            'cidade': forms.TextInput(attrs=css_attrs),
            'estado': forms.TextInput(attrs=css_attrs),
            'empresa': forms.Select(attrs=select_attrs),
        }

    def __init__(self, *args, **kwargs):
        user_empresa = kwargs.pop('empresa', None)
        super(UnidadeForm, self).__init__(*args, **kwargs)
        if user_empresa:
            self.fields['empresa'].queryset = Empresa.objects.filter(id=user_empresa.id)
            self.fields['empresa'].initial = user_empresa

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['nome', 'tipo_sensor', 'unidade', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs=css_attrs),
            'tipo_sensor': forms.TextInput(attrs=css_attrs),
            'unidade': forms.Select(attrs=select_attrs),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user_empresa = kwargs.pop('empresa', None)
        super(SensorForm, self).__init__(*args, **kwargs)
        if user_empresa:
            self.fields['unidade'].queryset = Unidade.objects.filter(empresa=user_empresa)

class RegistroUsuarioForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs=css_attrs), label="Nome de Usuário")
    email = forms.EmailField(widget=forms.EmailInput(attrs=css_attrs), label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput(attrs=css_attrs), label="Senha")
    
    cargo = forms.ChoiceField(
        choices=Perfil.CARGOS, 
        widget=forms.Select(attrs=select_attrs),
        label="Cargo / Nível de Acesso"
    )
    
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        widget=forms.Select(attrs=select_attrs),
        label="Vincular à Empresa",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        user_empresa = kwargs.pop('empresa', None)
        super(RegistroUsuarioForm, self).__init__(*args, **kwargs)

        if user_empresa:
            self.fields['empresa'].queryset = Empresa.objects.filter(id=user_empresa.id)
            self.fields['empresa'].initial = user_empresa
            self.fields['empresa'].widget = forms.HiddenInput() # Esconde o campo para o gestor

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Criptografa a senha!
        if commit:
            user.save()
        return user