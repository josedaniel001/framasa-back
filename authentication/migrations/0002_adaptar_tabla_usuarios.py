"""
Migración para adaptar la tabla usuarios existente a la estructura de Django
Agrega columnas que faltan de forma segura (solo si no existen)
"""
from django.db import migrations


def agregar_columnas_si_no_existen(apps, schema_editor):
    """Agregar columnas que Django necesita si no existen"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Verificar y agregar columnas si no existen
        columnas_a_agregar = [
            ("password", "VARCHAR(128) DEFAULT ''"),
            ("last_login", "TIMESTAMP NULL"),
            ("is_superuser", "BOOLEAN DEFAULT FALSE"),
            ("is_staff", "BOOLEAN DEFAULT FALSE"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("date_joined", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("first_name", "VARCHAR(150) DEFAULT ''"),
            ("last_name", "VARCHAR(150) DEFAULT ''"),
            ("fecha_creacion", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("fecha_actualizacion", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]
        
        for columna, tipo in columnas_a_agregar:
            try:
                # Verificar si la columna existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='usuarios' AND column_name=%s
                """, [columna])
                
                if not cursor.fetchone():
                    # Agregar la columna si no existe
                    cursor.execute(f'ALTER TABLE usuarios ADD COLUMN {columna} {tipo}')
                    print(f'Columna {columna} agregada')
                else:
                    print(f'Columna {columna} ya existe')
            except Exception as e:
                print(f'Error al agregar columna {columna}: {e}')


def revertir_cambios(apps, schema_editor):
    """No revertimos nada para mantener los datos"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(agregar_columnas_si_no_existen, revertir_cambios),
    ]

