# Generated migration for renaming costo_total_q to costo_estimado and adding costo_real

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('taller', '0006_add_orden_trabajo'),
    ]

    operations = [
        # Renombrar el campo costo_total_q a costo_estimado
        migrations.RenameField(
            model_name='ordentrabajo',
            old_name='costo_total_q',
            new_name='costo_estimado',
        ),
        # Cambiar el db_column del campo renombrado
        migrations.AlterField(
            model_name='ordentrabajo',
            name='costo_estimado',
            field=models.DecimalField(
                db_column='costo_estimado',
                decimal_places=2,
                default=0,
                help_text='Costo estimado en Quetzales',
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        # Agregar el nuevo campo costo_real
        migrations.AddField(
            model_name='ordentrabajo',
            name='costo_real',
            field=models.DecimalField(
                blank=True,
                db_column='costo_real',
                decimal_places=2,
                help_text='Costo real en Quetzales (calculado posteriormente)',
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
    ]

