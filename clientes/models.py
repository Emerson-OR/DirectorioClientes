from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    compania = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.compania})"

