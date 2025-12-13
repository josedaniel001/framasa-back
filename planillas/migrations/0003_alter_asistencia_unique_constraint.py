# Migration to change unique constraint to partial unique index
# This allows reusing the same employee+date combination when previous record is deactivated

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planillas', '0002_asistencia'),
    ]

    operations = [
        # Remove the existing unique constraint
        migrations.RemoveConstraint(
            model_name='asistencia',
            name='uq_asistencia_empleado_fecha',
        ),
        
        # Create a partial unique index that only applies when activo=true
        migrations.RunSQL(
            sql="""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_asistencia_empleado_fecha_activa
                ON public.asistencias (empleado_id, fecha)
                WHERE activo;
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS uq_asistencia_empleado_fecha_activa;
            """,
        ),
    ]

