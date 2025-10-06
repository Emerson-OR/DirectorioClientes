from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from clientes.models import Cliente

class Command(BaseCommand):
    help = 'Crea grupos (visualizador, administrador) y asigna permisos para Cliente'

    def handle(self, *args, **options):
        ct = ContentType.objects.get_for_model(Cliente)

        groups_permissions = {
            'visualizador': ['view_cliente'],
            'administrador': ['view_cliente', 'add_cliente', 'delete_cliente'],
        }

        for group_name, perm_codenames in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for codename in perm_codenames:
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Permiso {codename} no existe (aún).'))
            group.save()
            self.stdout.write(self.style.SUCCESS(f'Grupo "{group_name}" creado/actualizado.'))


