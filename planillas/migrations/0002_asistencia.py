# Generated migration for asistencias table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planillas', '0001_initial'),
        ('authentication', '0005_remove_usuario_rol_personalizado_alter_usuario_rol_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(db_column='fecha')),
                ('hora_entrada', models.TimeField(blank=True, db_column='hora_entrada', null=True)),
                ('hora_salida', models.TimeField(blank=True, db_column='hora_salida', null=True)),
                ('estado', models.CharField(
                    choices=[
                        ('Presente', 'Presente'),
                        ('Descanso', 'Descanso'),
                        ('Vacaciones', 'Vacaciones'),
                        ('Permiso con goce', 'Permiso con goce'),
                        ('Permiso sin goce', 'Permiso sin goce'),
                        ('Licencia Medica', 'Licencia Medica'),
                        ('Ausente', 'Ausente'),
                    ],
                    db_column='estado',
                    max_length=30
                )),
                ('fecha_retorno', models.DateField(blank=True, db_column='fecha_retorno', null=True)),
                ('observaciones', models.TextField(blank=True, db_column='observaciones', null=True)),
                ('activo', models.BooleanField(db_column='activo', default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at')),
                ('empleado', models.ForeignKey(
                    db_column='empleado_id',
                    on_delete=django.db.models.deletion.RESTRICT,
                    related_name='asistencias',
                    to='planillas.empleado'
                )),
                ('usuario', models.ForeignKey(
                    blank=True,
                    db_column='usuario_id',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='asistencias_registradas',
                    to='authentication.usuario'
                )),
            ],
            options={
                'verbose_name': 'Asistencia',
                'verbose_name_plural': 'Asistencias',
                'db_table': 'asistencias',
                'ordering': ['-fecha', '-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='asistencia',
            constraint=models.UniqueConstraint(fields=('empleado', 'fecha'), name='uq_asistencia_empleado_fecha'),
        ),
        migrations.AddConstraint(
            model_name='asistencia',
            constraint=models.CheckConstraint(
                check=models.Q(fecha_retorno__isnull=True) | models.Q(fecha_retorno__gte=models.F('fecha')),
                name='chk_fecha_retorno'
            ),
        ),
        migrations.AddIndex(
            model_name='asistencia',
            index=models.Index(fields=['empleado', 'fecha'], name='idx_asistencias_empleado_fecha'),
        ),
        migrations.AddIndex(
            model_name='asistencia',
            index=models.Index(fields=['estado'], name='idx_asistencias_estado'),
        ),
    ]

