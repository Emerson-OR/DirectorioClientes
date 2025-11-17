from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, Usuario
from .services.states_api import fetch_us_states


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
        base_classes = (
            'w-full bg-white text-black border border-[#b8975a]/30 '
            'rounded-lg px-3 py-2 focus:outline-none focus:ring-2 '
            'focus:ring-[#b8975a]/50 placeholder-gray-500'
        )

        # Aplicar clases comunes
        for key in self.fields:
            self.fields[key].widget.attrs.update({'class': base_classes})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'usuario'
        if commit:
            user.save()
        return user


# ----------------------------
# Formulario de cliente
# ----------------------------
class ClienteForm(forms.ModelForm):

    # Cambiamos pais → ChoiceField
    pais = forms.ChoiceField(
        required=False,
        label="Estado (USA)",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-[#0a0a0a] border border-[#3a3a3a] rounded-lg text-gray-200 input-focus-effect'
        })
    )

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

        # --------------------------
        # Cargar estados desde API
        # --------------------------
        estados = fetch_us_states()
        

        if estados:
            # → CORRECCIÓN: usar e["code"] y e["name"]
            self.fields['pais'].choices = [("", "Seleccione un estado")] + [
                (e["code"], f"{e['code']} - {e['name']}")
                for e in estados
            ]
        else:
            self.fields['pais'].choices = [("", "No disponible")]

        # Hacer no obligatorios todos excepto nombre
        for field_name, field in self.fields.items():
            if field_name != 'nombre':
                field.required = False
