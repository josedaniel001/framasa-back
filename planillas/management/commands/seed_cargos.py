from django.core.management.base import BaseCommand
from planillas.models import Cargo


class Command(BaseCommand):
    help = "Carga inicial de cargos (puestos) del sistema de planillas"

    def handle(self, *args, **options):
        cargos = [
            ("GERENTE_GENERAL", "Gerente General"),
            ("GERENTE_OPERACIONES", "Gerente de Operaciones"),
            ("SUPERVISOR", "Supervisor"),
            ("JEFE_PRODUCCION", "Jefe de Producción"),
            ("JEFE_BODEGA", "Jefe de Bodega"),
            ("OPERADOR_MAQUINARIA", "Operador de Maquinaria"),
            ("OPERADOR_PRODUCCION", "Operador de Producción"),
            ("CONDUCTOR", "Conductor"),
            ("AYUDANTE_PRODUCCION", "Ayudante de Producción"),
            ("MECANICO", "Mecánico"),
            ("VENDEDOR", "Vendedor"),
            ("CAJERO", "Cajero"),
        ]

        creados = 0
        existentes = 0

        for codigo, nombre in cargos:
            cargo, created = Cargo.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "activo": True,
                }
            )

            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Cargo creado: {nombre}"))
            else:
                existentes += 1
                self.stdout.write(self.style.WARNING(f"• Cargo ya existe: {nombre}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== Resumen ==="))
        self.stdout.write(f"✔ Creados: {creados}")
        self.stdout.write(f"• Existentes: {existentes}")