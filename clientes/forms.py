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
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-white text-black border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50 placeholder-gray-500',
                'placeholder': 'Nombre de usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-white text-black border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50 placeholder-gray-500',
                'placeholder': 'usuario@empresa.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = 'w-full bg-white text-black border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50 placeholder-gray-500'
        # Asegurar estilos en todos los campos, incluidos password1/password2 que no son de modelo
        self.fields['username'].widget.attrs.update({
            'class': base_classes,
            'placeholder': self.fields['username'].widget.attrs.get('placeholder', 'Nombre de usuario')
        })
        if 'email' in self.fields:
            self.fields['email'].widget.attrs.update({
                'class': base_classes,
                'placeholder': self.fields['email'].widget.attrs.get('placeholder', 'usuario@empresa.com')
            })
        self.fields['password1'].widget.attrs.update({
            'class': base_classes,
            'placeholder': self.fields['password1'].widget.attrs.get('placeholder', 'Mínimo 8 caracteres')
        })
        self.fields['password2'].widget.attrs.update({
            'class': base_classes,
            'placeholder': self.fields['password2'].widget.attrs.get('placeholder', 'Repite tu contraseña')
        })

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
            'nombre': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a]/80 text-gray-200 border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50',
                'placeholder': 'Nombre completo'
            }),
            'compania': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a]/80 text-gray-200 border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50',
                'placeholder': 'Nombre de la compañía'
            }),
            'identificacion': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a]/80 text-gray-200 border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50',
                'placeholder': 'Código o identificación'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'w-full bg-[#1a1a1a]/80 text-gray-200 border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50',
                'placeholder': 'Correo electrónico'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a]/80 text-gray-200 border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50',
                'placeholder': 'País'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a]/80 text-gray-200 border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50',
                'placeholder': 'Dirección del cliente'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'w-full bg-[#1a1a1a]/80 text-gray-200 border border-[#b8975a]/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#b8975a]/50'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'nombre':  # nombre sigue siendo obligatorio
                field.required = False
