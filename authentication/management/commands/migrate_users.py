"""
Comando de Django para migrar usuarios existentes desde PostgreSQL a Django
Uso: python manage.py migrate_users
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model
import bcrypt

User = get_user_model()


class Command(BaseCommand):
    help = 'Migra usuarios existentes desde la tabla usuarios de PostgreSQL a Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-passwords',
            action='store_true',
            help='Resetear contraseñas de usuarios migrados (requerirá cambio en primer login)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando migración de usuarios...'))
        
        reset_passwords = options['reset_passwords']
        
        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuarios'
                );
            """)
            
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                self.stdout.write(
                    self.style.WARNING('La tabla "usuarios" no existe. Saltando migración.')
                )
                return
            
            # Obtener todos los usuarios
            cursor.execute("""
                SELECT id, username, email, password_hash, rol, activo 
                FROM usuarios
            """)
            
            users = cursor.fetchall()
            self.stdout.write(f'Encontrados {len(users)} usuarios para migrar.')
            
            migrated = 0
            skipped = 0
            errors = 0
            
            for user_data in users:
                user_id, username, email, password_hash, rol, activo = user_data
                
                try:
                    # Verificar si el usuario ya existe
                    if User.objects.filter(username=username).exists():
                        self.stdout.write(
                            self.style.WARNING(f'Usuario {username} ya existe. Saltando...')
                        )
                        skipped += 1
                        continue
                    
                    # Crear el usuario
                    user = User(
                        username=username,
                        email=email or f'{username}@framasa.com',
                        rol=rol or 'vendedor',
                        activo=activo if activo is not None else True,
                        is_active=activo if activo is not None else True,
                    )
                    
                    # Manejar la contraseña
                    if reset_passwords:
                        # Establecer una contraseña temporal que el usuario debe cambiar
                        user.set_password('Cambiar123!')
                        user.save()
                        self.stdout.write(
                            self.style.WARNING(
                                f'Usuario {username} creado con contraseña temporal: Cambiar123!'
                            )
                        )
                    else:
                        # Intentar usar el hash existente
                        # Nota: Django usa PBKDF2, pero si las contraseñas fueron creadas con bcrypt,
                        # necesitarás resetearlas o usar un método de autenticación personalizado
                        user.set_password('temp_password_needs_reset')
                        user.save()
                        # Actualizar directamente el password_hash en la base de datos
                        # Esto es un workaround - idealmente deberías resetear las contraseñas
                        cursor.execute("""
                            UPDATE auth_user 
                            SET password = %s 
                            WHERE id = %s
                        """, [password_hash, user.id])
                        
                        self.stdout.write(
                            self.style.WARNING(
                                f'Usuario {username} migrado. NOTA: Puede necesitar resetear contraseña.'
                            )
                        )
                    
                    migrated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Usuario {username} migrado exitosamente')
                    )
                    
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error al migrar usuario {username}: {str(e)}')
                    )
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*50))
            self.stdout.write(self.style.SUCCESS(f'Migración completada:'))
            self.stdout.write(self.style.SUCCESS(f'  - Migrados: {migrated}'))
            self.stdout.write(self.style.SUCCESS(f'  - Omitidos: {skipped}'))
            self.stdout.write(self.style.SUCCESS(f'  - Errores: {errors}'))
            
            if not reset_passwords:
                self.stdout.write(
                    self.style.WARNING(
                        '\nNOTA: Las contraseñas pueden no funcionar correctamente porque '
                        'Django usa PBKDF2 y las contraseñas originales pueden usar bcrypt. '
                        'Considera usar --reset-passwords para establecer contraseñas temporales.'
                    )
                )

