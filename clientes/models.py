from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models.fields.files import FieldFile
from django.utils import timezone  # 👈 para manejar zona horaria

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
            return timezone.localtime(self.fecha_eliminacion).strftime('%Y-%m-%d %H:%M')
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

    def save(self, *args, usuario=None, **kwargs):
        if self.pk:
            old = Cliente.objects.get(pk=self.pk)
            cambios = []

            for field in self._meta.fields:
                field_name = field.name
                old_value = getattr(old, field_name)
                new_value = getattr(self, field_name)

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

    def __str__(self):
        return f"{self.cliente.nombre} - {self.campo} cambiado por {self.editado_por} el {self.fecha_edicion_formateada}"

    @property
    def fecha_edicion_formateada(self):
        return timezone.localtime(self.fecha_edicion).strftime('%Y-%m-%d %H:%M')

