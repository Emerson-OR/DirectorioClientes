from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models.fields.files import FieldFile
from django.utils import timezone
import pytz
import os
from django.conf import settings

# -------------------------------
# Usuario personalizado
# -------------------------------
class Usuario(AbstractUser):
    ROLES = (
        ('usuario', 'Usuario'),
        ('admin', 'Administrador'),
        ('superadmin', 'Superadministrador'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

# -------------------------------
# Cliente
# -------------------------------
class Cliente(models.Model):
    codigo_cliente = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=100)
    compania = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50)
    correo = models.EmailField(blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.compania})"

    @property
    def fecha_eliminacion_formateada(self):
        if self.fecha_eliminacion:
            colombia_tz = pytz.timezone('America/Bogota')
            fecha_colombia = timezone.localtime(self.fecha_eliminacion, colombia_tz)
            return fecha_colombia.strftime('%d-%m-%Y, %I:%M %p')
        return None

    @property
    def actualizado_en_formateado(self):
        if self.actualizado_en:
            colombia_tz = pytz.timezone('America/Bogota')
            fecha_colombia = timezone.localtime(self.actualizado_en, colombia_tz)
            return fecha_colombia.strftime('%d-%m-%Y, %I:%M %p')
        return None

    @property
    def google_maps_link(self):
        if self.direccion:
            query = self.direccion
        elif self.pais:
            query = self.pais
        else:
            return None
        return f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"

    @property
    def logo_url(self):
        """
        Devuelve la URL del logo si existe en el campo ImageField.
        Si no hay logo cargado, intenta buscar un archivo en media/logos
        con el identificador del cliente y extensiones comunes.
        """
        try:
            if self.logo and hasattr(self.logo, 'url') and self.logo.url:
                return self.logo.url
        except Exception:
            # Si el archivo referenciado no existe en disco, continuamos con el fallback
            pass

        # Fallback: buscar por identificacion en media/logos
        if not self.identificacion:
            return None

        posibles_ext = ('.png', '.jpg', '.jpeg', '.webp')
        for ext in posibles_ext:
            disco_path = os.path.join(settings.MEDIA_ROOT, 'logos', f"{self.identificacion}{ext}")
            if os.path.exists(disco_path):
                return settings.MEDIA_URL + f"logos/{self.identificacion}{ext}"
        return None

    def save(self, *args, usuario=None, **kwargs):
        """
        Sobrescribe save() para:
        1️⃣ Eliminar microsegundos de fechas.
        2️⃣ Registrar historial solo de campos relevantes.
        """
        # 🔹 Formatear las fechas
        if self.fecha_eliminacion:
            self.fecha_eliminacion = self.fecha_eliminacion.replace(microsecond=0)
        if self.creado_en:
            self.creado_en = self.creado_en.replace(microsecond=0)
        self.actualizado_en = timezone.now().replace(microsecond=0)

        # 🔹 Solo registrar historial si el objeto ya existe
        if self.pk:
            old = Cliente.objects.get(pk=self.pk)
            cambios = []

            # Campos que no queremos en historial
            campos_ignorar = ['creado_en', 'actualizado_en', 'activo']

            for field in self._meta.fields:
                field_name = field.name
                if field_name in campos_ignorar:
                    continue

                old_value = getattr(old, field_name)
                new_value = getattr(self, field_name)

                # Comparar FieldFile
                if isinstance(old_value, FieldFile):
                    old_str = old_value.name if old_value else ''
                    new_str = new_value.name if new_value else ''
                    cambio_real = old_str != new_str
                else:
                    old_str = str(old_value) if old_value is not None else ''
                    new_str = str(new_value) if new_value is not None else ''
                    cambio_real = old_str != new_str

                if cambio_real:
                    cambios.append((field_name, old_str, new_str))

            # Crear historial solo para cambios reales
            for campo, anterior, nuevo in cambios:
                HistorialCliente.objects.create(
                    cliente=self,
                    campo=campo,
                    valor_anterior=anterior,
                    valor_nuevo=nuevo,
                    editado_por=usuario or self.creado_por
                )

        super().save(*args, **kwargs)

# -------------------------------
# Historial del cliente
# -------------------------------
class HistorialCliente(models.Model):
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='historial'
    )
    campo = models.CharField(max_length=50)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_nuevo = models.TextField(null=True, blank=True)
    editado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True
    )
    fecha_edicion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 🔹 Elimina microsegundos antes de guardar
        if not self.fecha_edicion:
            self.fecha_edicion = timezone.now().replace(microsecond=0)
        else:
            self.fecha_edicion = self.fecha_edicion.replace(microsecond=0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente.nombre} - {self.campo} cambiado por {self.editado_por} el {self.fecha_edicion_formateada}"

    @property
    def fecha_edicion_formateada(self):
        """Retorna la fecha en formato colombiano: DD-MM-YYYY, HH:MM AM/PM"""
        colombia_tz = pytz.timezone('America/Bogota')
        fecha_colombia = timezone.localtime(self.fecha_edicion, colombia_tz)
        return fecha_colombia.strftime('%d-%m-%Y, %I:%M %p')

# -------------------------------
# Registro de usuarios creados por administradores
# -------------------------------
class UsuarioCreado(models.Model):
    creador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_usuarios_creados'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='registro_de_creacion'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        creador = self.creador.username if self.creador else 'desconocido'
        return f"{self.usuario.username} creado por {creador}"
