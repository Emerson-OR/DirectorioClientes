from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo de usuario personalizado con roles
class Usuario(AbstractUser):
    ROLES = (
        ('usuario', 'Usuario'),
        ('admin', 'Administrador'),
        ('superadmin', 'Superadministrador'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


# Modelo Cliente vinculado al usuario creador
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    compania = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    activo = models.BooleanField(default=True)  # 🔹 Nuevo campo
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
    def google_maps_link(self):
        """
        Genera automáticamente un enlace de Google Maps a partir de la dirección o país.
        """
        if self.direccion:
            query = self.direccion
        elif self.pais:
            query = self.pais
        else:
            return None
        return f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"
