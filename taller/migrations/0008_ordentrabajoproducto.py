# Generated migration for OrdenTrabajoProducto model

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('taller', '0007_rename_costo_add_costo_real'),
        ('ferreteria', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdenTrabajoProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(
                    db_column='cantidad',
                    help_text='Cantidad del producto a usar',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('precio_unitario', models.DecimalField(
                    blank=True,
                    db_column='precio_unitario',
                    decimal_places=2,
                    help_text='Precio unitario del producto al momento de agregarlo',
                    max_digits=12,
                    null=True
                )),
                ('costo_total', models.DecimalField(
                    blank=True,
                    db_column='costo_total',
                    decimal_places=2,
                    help_text='Costo total (cantidad x precio_unitario)',
                    max_digits=12,
                    null=True
                )),
                ('descontado_inventario', models.BooleanField(
                    db_column='descontado_inventario',
                    default=False,
                    help_text='Indica si ya se descontó del inventario de ferretería'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at')),
                ('orden_trabajo', models.ForeignKey(
                    db_column='orden_trabajo_id',
                    help_text='Orden de trabajo a la que pertenece este producto',
                    on_delete=django.db.models.deletion.RESTRICT,
                    related_name='productos_orden',
                    to='taller.ordentrabajo'
                )),
                ('producto', models.ForeignKey(
                    db_column='producto_id',
                    help_text='Producto de ferretería usado en la orden',
                    on_delete=django.db.models.deletion.RESTRICT,
                    related_name='ordenes_trabajo',
                    to='ferreteria.producto'
                )),
                ('movimiento_inventario', models.ForeignKey(
                    blank=True,
                    db_column='movimiento_inventario_id',
                    help_text='Referencia al movimiento de inventario generado',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='ordenes_trabajo_productos',
                    to='ferreteria.movimientoinventario'
                )),
            ],
            options={
                'db_table': 'ordenes_trabajo_productos',
                'verbose_name': 'Producto de Orden de Trabajo',
                'verbose_name_plural': 'Productos de Órdenes de Trabajo',
                'ordering': ['orden_trabajo', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='ordentrabajoproducto',
            index=models.Index(fields=['orden_trabajo'], name='idx_otp_orden_trabajo'),
        ),
        migrations.AddIndex(
            model_name='ordentrabajoproducto',
            index=models.Index(fields=['producto'], name='idx_otp_producto'),
        ),
        migrations.AddIndex(
            model_name='ordentrabajoproducto',
            index=models.Index(fields=['descontado_inventario'], name='idx_otp_descontado'),
        ),
    ]

