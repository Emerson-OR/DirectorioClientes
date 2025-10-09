from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, Usuario

# ----------------------------
# Formulario de registro de usuario
# ----------------------------
class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'usuario'  # Rol por defecto
        if commit:
            user.save()
        return user


# ----------------------------
# Formulario de cliente (ampliado)
# ----------------------------
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'compania',
            'identificacion',
            'correo',
            'pais',
            'direccion',
            'logo',
        ]
        labels = {
            'nombre': 'Nombre del Cliente',
            'compania': 'Compañía',
            'identificacion': 'Código o ID',
            'correo': 'Correo Electrónico',
            'pais': 'País',
            'direccion': 'Dirección',
            'logo': 'Logo del Cliente',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'compania': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la compañía'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código o identificación'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección del cliente'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # Sobrescribir __init__ para hacer campos opcionales
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'nombre':  # nombre sigue siendo obligatorio
                field.required = False

