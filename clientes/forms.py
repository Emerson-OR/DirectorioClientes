from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, Usuario

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'usuario'  # 🔹 Asignamos rol por defecto
        if commit:
            user.save()
        return user



# Formulario de cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'compania', 'identificacion', 'logo']
