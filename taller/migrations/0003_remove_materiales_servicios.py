# Generated manually to remove materiales and servicios tables

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taller', '0002_servicio_serviciomaterial_tipoequipo_and_more'),
    ]

    operations = [
        # Eliminar primero la tabla intermedia (tiene foreign keys)
        migrations.DeleteModel(
            name='ServicioMaterial',
        ),
        # Luego eliminar Servicio (tiene foreign key a MaterialTaller a través de ManyToMany)
        migrations.DeleteModel(
            name='Servicio',
        ),
        # Eliminar categorías y tipos de equipo
        migrations.DeleteModel(
            name='CategoriaServicio',
        ),
        migrations.DeleteModel(
            name='TipoEquipo',
        ),
        # Finalmente eliminar MaterialTaller
        migrations.DeleteModel(
            name='MaterialTaller',
        ),
    ]

