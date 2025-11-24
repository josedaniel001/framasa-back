"""
Comando de Django para poblar categorías de productos
Uso: python manage.py populate_categorias
"""
from django.core.management.base import BaseCommand
from ferreteria.models import CategoriaProducto


class Command(BaseCommand):
    help = 'Pobla la base de datos con categorías de productos comunes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todas las categorías existentes antes de poblar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando población de categorías...'))
        
        reset = options['reset']
        
        if reset:
            self.stdout.write(self.style.WARNING('Eliminando categorías existentes...'))
            CategoriaProducto.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Categorías eliminadas.'))
        
        # Lista de categorías comunes para ferretería
        categorias = [
            {
                'nombre': 'Herramientas Manuales',
                'descripcion': 'Martillos, destornilladores, alicates, llaves, etc.'
            },
            {
                'nombre': 'Herramientas Eléctricas',
                'descripcion': 'Taladros, sierras eléctricas, pulidoras, etc.'
            },
            {
                'nombre': 'Materiales de Construcción',
                'descripcion': 'Cemento, ladrillos, bloques, arena, grava, etc.'
            },
            {
                'nombre': 'Pinturas y Barnices',
                'descripcion': 'Pinturas, barnices, diluyentes, brochas, rodillos, etc.'
            },
            {
                'nombre': 'Fontanería',
                'descripcion': 'Tuberías, conexiones, grifos, válvulas, etc.'
            },
            {
                'nombre': 'Electricidad',
                'descripcion': 'Cables, interruptores, tomas, focos, etc.'
            },
            {
                'nombre': 'Ferretería General',
                'descripcion': 'Tornillos, clavos, tuercas, arandelas, etc.'
            },
            {
                'nombre': 'Jardinería',
                'descripcion': 'Herramientas de jardín, mangueras, semillas, etc.'
            },
            {
                'nombre': 'Seguridad',
                'descripcion': 'Candados, cerraduras, alarmas, etc.'
            },
            {
                'nombre': 'Limpieza',
                'descripcion': 'Escobas, trapeadores, detergentes, etc.'
            },
            {
                'nombre': 'Adhesivos y Selladores',
                'descripcion': 'Pegamentos, siliconas, cintas adhesivas, etc.'
            },
            {
                'nombre': 'Cristalería',
                'descripcion': 'Vidrios, espejos, cristales, etc.'
            },
        ]
        
        creadas = 0
        actualizadas = 0
        
        for cat_data in categorias:
            categoria, created = CategoriaProducto.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={
                    'descripcion': cat_data['descripcion'],
                    'activo': True
                }
            )
            
            if created:
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Categoría creada: {categoria.nombre}')
                )
            else:
                # Actualizar descripción si existe pero no tiene descripción
                if not categoria.descripcion and cat_data['descripcion']:
                    categoria.descripcion = cat_data['descripcion']
                    categoria.activo = True
                    categoria.save()
                    actualizadas += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Categoría actualizada: {categoria.nombre}')
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(f'- Categoría ya existe: {categoria.nombre}')
                    )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado: {creadas} categorías creadas, '
                f'{actualizadas} actualizadas'
            )
        )
        self.stdout.write(self.style.SUCCESS('=' * 60))

