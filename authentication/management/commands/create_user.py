"""
Comando de Django para crear usuarios fácilmente
Uso: python manage.py create_user <username> <email> <password> <rol>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un nuevo usuario en el sistema'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario')
        parser.add_argument('email', type=str, help='Email del usuario')
        parser.add_argument('password', type=str, help='Contraseña del usuario')
        parser.add_argument(
            'rol',
            type=str,
            choices=['admin', 'gerente', 'vendedor', 'operador'],
            help='Rol del usuario'
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Crear como superusuario (admin de Django)',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        rol = options['rol']
        is_superuser = options['superuser']
        
        try:
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.ERROR(f'Error: El usuario "{username}" ya existe.')
                )
                return
            
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.ERROR(f'Error: El email "{email}" ya está en uso.')
                )
                return
            
            # Crear el usuario
            user = User(
                username=username,
                email=email,
                rol=rol,
                activo=True,
                is_staff=is_superuser,
                is_superuser=is_superuser,
            )
            user.set_password(password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Usuario "{username}" creado exitosamente con rol "{rol}"'
                )
            )
            
            if is_superuser:
                self.stdout.write(
                    self.style.SUCCESS('  (Superusuario - acceso al admin de Django)')
                )
                
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Error de validación: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al crear usuario: {e}'))

