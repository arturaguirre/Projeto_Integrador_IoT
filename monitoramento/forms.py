from django import forms
from django.contrib.auth.models import User
from .models import Empresa, Unidade, Sensor

# Atributos de estilo para todos os campos (Tema Dark)
css_attrs = {'class': 'form-control bg-dark text-white border-secondary'}

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'cnpj', 'email', 'telefone', 'endereco']
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

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs=css_attrs))
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs=css_attrs),
            'email': forms.EmailInput(attrs=css_attrs),
        }