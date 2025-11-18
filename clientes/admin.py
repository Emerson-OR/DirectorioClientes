from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Cliente, HistorialCliente
from django.utils.html import format_html


# ============================
# CONFIGURACIÓN DEL MODELO CLIENTE
# ============================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'compania', 'identificacion', 'logo_tag', 'creado_por', 'creado_en')
    search_fields = ('nombre', 'compania', 'identificacion')

    def logo_tag(self, obj):
        url = getattr(obj, 'logo_url', None)
        if url:
            return format_html('<img src="{}" width="50" />', url)
        return '-'
    logo_tag.short_description = 'Logo'


# ============================
# CONFIGURACIÓN DEL MODELO USUARIO
# ============================
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'is_active', 'is_staff')
    list_filter = ('rol', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Rol y permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def get_readonly_fields(self, request, obj=None):
        """Evita que los no-superadmins modifiquen roles"""
        if not request.user.is_authenticated:
            return self.readonly_fields

        # Si no es superadmin, no puede modificar el campo 'rol'
        if not request.user.is_superuser or request.user.rol != 'superadmin':
            return self.readonly_fields + ('rol', 'is_staff', 'is_superuser')
        return self.readonly_fields

# ============================
# CONFIGURACIÓN DEL MODELO HISTORIALCLIENTE
# ============================
@admin.register(HistorialCliente)
class HistorialClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'campo', 'valor_anterior', 'valor_nuevo', 'editado_por', 'fecha_edicion')
    list_filter = ('fecha_edicion', 'campo', 'editado_por')
    search_fields = ('cliente__nombre', 'campo', 'valor_anterior', 'valor_nuevo')