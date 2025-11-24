"""
Comando de Django para poblar unidades de medida
Uso: python manage.py populate_unidades_medida
"""
from django.core.management.base import BaseCommand
from ferreteria.models import UnidadMedida


class Command(BaseCommand):
    help = 'Pobla la base de datos con unidades de medida comunes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todas las unidades de medida existentes antes de poblar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando población de unidades de medida...'))
        
        reset = options['reset']
        
        if reset:
            self.stdout.write(self.style.WARNING('Eliminando unidades de medida existentes...'))
            UnidadMedida.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Unidades de medida eliminadas.'))
        
        # Lista de unidades de medida comunes para ferretería
        unidades = [
            # Unidades de peso
            {'nombre': 'Kilogramo', 'abreviatura': 'kg'},
            {'nombre': 'Gramo', 'abreviatura': 'g'},
            {'nombre': 'Libra', 'abreviatura': 'lb'},
            {'nombre': 'Onza', 'abreviatura': 'oz'},
            {'nombre': 'Tonelada', 'abreviatura': 'ton'},
            
            # Unidades de longitud
            {'nombre': 'Metro', 'abreviatura': 'm'},
            {'nombre': 'Centímetro', 'abreviatura': 'cm'},
            {'nombre': 'Milímetro', 'abreviatura': 'mm'},
            {'nombre': 'Pie', 'abreviatura': 'ft'},
            {'nombre': 'Pulgada', 'abreviatura': 'in'},
            {'nombre': 'Yarda', 'abreviatura': 'yd'},
            
            # Unidades de volumen
            {'nombre': 'Litro', 'abreviatura': 'L'},
            {'nombre': 'Mililitro', 'abreviatura': 'mL'},
            {'nombre': 'Galón', 'abreviatura': 'gal'},
            {'nombre': 'Metro Cúbico', 'abreviatura': 'm³'},
            {'nombre': 'Centímetro Cúbico', 'abreviatura': 'cm³'},
            {'nombre': 'Pie Cúbico', 'abreviatura': 'ft³'},
            
            # Unidades de área
            {'nombre': 'Metro Cuadrado', 'abreviatura': 'm²'},
            {'nombre': 'Centímetro Cuadrado', 'abreviatura': 'cm²'},
            {'nombre': 'Pie Cuadrado', 'abreviatura': 'ft²'},
            
            # Unidades de cantidad/piezas
            {'nombre': 'Pieza', 'abreviatura': 'pz'},
            {'nombre': 'Unidad', 'abreviatura': 'und'},
            {'nombre': 'Par', 'abreviatura': 'par'},
            {'nombre': 'Docena', 'abreviatura': 'doc'},
            {'nombre': 'Ciento', 'abreviatura': 'cto'},
            {'nombre': 'Millar', 'abreviatura': 'mil'},
            {'nombre': 'Caja', 'abreviatura': 'caja'},
            {'nombre': 'Paquete', 'abreviatura': 'pqt'},
            {'nombre': 'Bolsa', 'abreviatura': 'bolsa'},
            {'nombre': 'Rollo', 'abreviatura': 'rollo'},
            {'nombre': 'Tubo', 'abreviatura': 'tubo'},
            {'nombre': 'Botella', 'abreviatura': 'bot'},
            {'nombre': 'Frasco', 'abreviatura': 'frasco'},
            {'nombre': 'Bidón', 'abreviatura': 'bidón'},
            {'nombre': 'Tambor', 'abreviatura': 'tambor'},
            
            # Unidades especiales
            {'nombre': 'Kit', 'abreviatura': 'kit'},
            {'nombre': 'Juego', 'abreviatura': 'juego'},
            {'nombre': 'Set', 'abreviatura': 'set'},
        ]
        
        creadas = 0
        actualizadas = 0
        
        for unidad_data in unidades:
            unidad, created = UnidadMedida.objects.get_or_create(
                nombre=unidad_data['nombre'],
                defaults={
                    'abreviatura': unidad_data['abreviatura'],
                    'activo': True
                }
            )
            
            if created:
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Unidad creada: {unidad.nombre} ({unidad.abreviatura})'
                    )
                )
            else:
                # Actualizar abreviatura si existe pero no tiene o es diferente
                if unidad.abreviatura != unidad_data['abreviatura']:
                    unidad.abreviatura = unidad_data['abreviatura']
                    unidad.activo = True
                    unidad.save()
                    actualizadas += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'↻ Unidad actualizada: {unidad.nombre} ({unidad.abreviatura})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'- Unidad ya existe: {unidad.nombre} ({unidad.abreviatura})'
                        )
                    )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado: {creadas} unidades creadas, '
                f'{actualizadas} actualizadas'
            )
        )
        self.stdout.write(self.style.SUCCESS('=' * 60))

