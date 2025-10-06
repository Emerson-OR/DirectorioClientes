from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, Usuario

# Formulario de registro de usuario
class RegistroForm(UserCreationForm):
    rol = forms.ChoiceField(choices=Usuario.ROLES)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'password1', 'password2']

# Formulario de cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'compania', 'identificacion', 'logo']

