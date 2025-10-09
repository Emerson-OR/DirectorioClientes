from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from clientes.models import Cliente

class Command(BaseCommand):
    help = 'Elimina definitivamente los clientes que llevan más de 30 días inactivos.'

    def handle(self, *args, **kwargs):
        limite = timezone.now() - timedelta(days=30)
        clientes_a_borrar = Cliente.objects.filter(activo=False, fecha_eliminacion__lte=limite)

        count = clientes_a_borrar.count()
        clientes_a_borrar.delete()

        self.stdout.write(self.style.SUCCESS(f'{count} clientes eliminados definitivamente.'))
