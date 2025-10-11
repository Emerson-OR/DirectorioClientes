# clientes/management/commands/limpiar_duplicados.py

from django.core.management.base import BaseCommand
from clientes.models import Cliente
from django.db.models import Count

class Command(BaseCommand):
    help = 'Encuentra y elimina clientes con ID de identificación duplicados, conservando el más reciente.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Iniciando limpieza de clientes duplicados ---"))

        # 1. Encontrar los valores de 'identificacion' que están duplicados
        duplicados = (
            Cliente.objects.values('identificacion')
            .annotate(count=Count('id'))
            .order_by()
            .filter(count__gt=1)
        )

        if not duplicados.exists():
            self.stdout.write(self.style.SUCCESS("✅ No se encontraron clientes con ID de identificación duplicados."))
            return

        self.stdout.write(self.style.WARNING(f"Se encontraron {len(duplicados)} IDs de identificación con registros duplicados."))
        
        total_eliminados = 0
        # 2. Iterar sobre cada 'identificacion' duplicada
        for item in duplicados:
            identificacion = item['identificacion']
            
            # 3. Obtener todos los clientes que comparten la misma 'identificacion', ordenados por fecha de creación descendente
            clientes_duplicados = Cliente.objects.filter(identificacion=identificacion).order_by('-creado_en')
            
            # El primer objeto es el más reciente, así que lo conservamos
            cliente_a_conservar = clientes_duplicados.first()
            self.stdout.write(f"\nProcesando ID '{identificacion}':")
            self.stdout.write(f"  - Conservando el registro más reciente: '{cliente_a_conservar.nombre}' (Creado en: {cliente_a_conservar.creado_en.strftime('%Y-%m-%d %H:%M:%S')})")
            
            # Los demás registros (desde el segundo en adelante) se eliminarán
            clientes_a_eliminar = clientes_duplicados[1:]
            
            num_a_eliminar = len(clientes_a_eliminar)
            if num_a_eliminar > 0:
                for cliente in clientes_a_eliminar:
                    self.stdout.write(f"    - Eliminando registro obsoleto: '{cliente.nombre}' (ID de objeto: {cliente.id})")
                    cliente.delete()
                total_eliminados += num_a_eliminar

        if total_eliminados > 0:
            self.stdout.write(self.style.SUCCESS(f"\n🎉 Limpieza completada. Se eliminaron {total_eliminados} registros duplicados."))
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ No fue necesario eliminar registros."))
