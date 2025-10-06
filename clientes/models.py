from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo de usuario personalizado con roles
class Usuario(AbstractUser):
    ROLES = (
        ('viewer', 'Visualizador'),
        ('admin', 'Administrador'),
        ('superadmin', 'Superadministrador'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='viewer')

# Modelo Cliente vinculado a usuario creador
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    compania = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='clientes_creados')

    def __str__(self):
        return f"{self.nombre} ({self.compania})"

