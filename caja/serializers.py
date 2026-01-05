from rest_framework import serializers
from .models import MovimientoCaja, MovimientoCajaDetalle


class MovimientoCajaDetalleSerializer(serializers.ModelSerializer):
    unidad_medida_nombre = serializers.CharField(source='unidad_medida.nombre', read_only=True, required=False)
    unidad_medida_abreviatura = serializers.CharField(source='unidad_medida.abreviatura', read_only=True, required=False)
    
    class Meta:
        model = MovimientoCajaDetalle
        fields = '__all__'
        read_only_fields = ('created_at',)


class MovimientoCajaDetalleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear detalles sin el movimiento (se asigna automáticamente)"""
    class Meta:
        model = MovimientoCajaDetalle
        fields = ['producto_nombre', 'cantidad', 'unidad_medida', 'costo_total']


class MovimientoCajaSerializer(serializers.ModelSerializer):
    detalles = MovimientoCajaDetalleSerializer(many=True, read_only=True)
    detalles_create = MovimientoCajaDetalleCreateSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = MovimientoCaja
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles_create', [])
        movimiento = MovimientoCaja.objects.create(**validated_data)
        
        # Crear los detalles
        for detalle_data in detalles_data:
            MovimientoCajaDetalle.objects.create(movimiento=movimiento, **detalle_data)
        
        return movimiento
    
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles_create', None)
        
        # Actualizar campos del movimiento
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Si se proporcionan nuevos detalles, eliminar los antiguos y crear los nuevos
        if detalles_data is not None:
            # Eliminar detalles existentes
            instance.detalles.all().delete()
            # Crear nuevos detalles
            for detalle_data in detalles_data:
                MovimientoCajaDetalle.objects.create(movimiento=instance, **detalle_data)
        
        return instance

