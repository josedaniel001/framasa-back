from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('El usuario debe tener un username')
        email = self.normalize_email(email) if email else f'{username}@framasa.com'
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado adaptado a la estructura existente
    """
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('operador', 'Operador'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='vendedor')
    activo = models.BooleanField(default=True)
    
    # Campos requeridos por Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Campos opcionales
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Campos personalizados
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.username
    
    def get_short_name(self):
        return self.first_name or self.username


class ConfiguracionRol(models.Model):
    """
    Modelo para gestionar la configuración de permisos de los roles básicos
    """
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('operador', 'Operador'),
    ]
    
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        unique=True,
        verbose_name='Rol',
        help_text='Rol básico del sistema'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción',
        help_text='Descripción de las funciones y responsabilidades de este rol'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si este rol está activo en el sistema'
    )
    
    # Permisos asociados al rol
    permisos = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='configuraciones_rol',
        verbose_name='Permisos',
        help_text='Permisos asociados a este rol'
    )
    
    # Grupos de Django asociados
    grupos = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='configuraciones_rol',
        verbose_name='Grupos de Django',
        help_text='Grupos de Django asociados a este rol'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        db_table = 'configuraciones_rol'
        verbose_name = 'Configuración de Rol'
        verbose_name_plural = 'Configuraciones de Roles'
        ordering = ['rol']
    
    def __str__(self):
        return self.get_rol_display()
    
    def get_permisos_list(self):
        """Retorna lista de nombres de permisos"""
        return [p.codename for p in self.permisos.all()]
    
    def get_num_usuarios(self):
        """Retorna el número de usuarios con este rol"""
        # Usar get_user_model para evitar importación circular
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(rol=self.rol).count()