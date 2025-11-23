from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario
    """
    # Campos opcionales que pueden no existir en tablas antiguas
    activo = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'rol', 'activo', 'first_name', 'last_name')
        read_only_fields = ('id',)
    
    def get_activo(self, obj):
        """Obtener el campo activo si existe, sino usar is_active"""
        if hasattr(obj, 'activo'):
            return obj.activo
        return obj.is_active
    
    def get_rol(self, obj):
        """Obtener el campo rol si existe, sino usar 'vendedor' por defecto"""
        if hasattr(obj, 'rol') and obj.rol:
            return obj.rol
        return 'vendedor'


class LoginSerializer(serializers.Serializer):
    """
    Serializer para el login
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Credenciales incorrectas.')
            
            if not user.is_active:
                raise serializers.ValidationError('Usuario inactivo.')
            
            # Verificar campo activo si existe (puede no existir en tablas antiguas)
            if hasattr(user, 'activo') and not user.activo:
                raise serializers.ValidationError('Usuario inactivo.')
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Debe incluir "username" y "password".')

        return attrs

