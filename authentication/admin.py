from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission, Group
from django.utils.html import format_html
from .models import Usuario, ConfiguracionRol


@admin.register(ConfiguracionRol)
class ConfiguracionRolAdmin(admin.ModelAdmin):
    """
    Admin para gestionar la configuración de permisos de los roles básicos
    """
    list_display = ('get_rol_display', 'activo', 'num_permisos', 'num_usuarios', 'fecha_actualizacion')
    list_filter = ('rol', 'activo', 'fecha_actualizacion')
    search_fields = ('descripcion',)
    filter_horizontal = ('permisos', 'grupos')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'num_permisos', 'num_usuarios')
    
    fieldsets = (
        ('Información del Rol', {
            'fields': ('rol', 'descripcion', 'activo'),
            'description': 'Configure los permisos para este rol básico del sistema'
        }),
        ('Permisos', {
            'fields': ('permisos',),
            'description': 'Seleccione los permisos que tendrán automáticamente los usuarios con este rol'
        }),
        ('Grupos de Django', {
            'fields': ('grupos',),
            'description': 'Opcional: Asocie grupos de Django a este rol para integración con permisos del sistema'
        }),
        ('Estadísticas', {
            'fields': ('num_permisos', 'num_usuarios'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_rol_display(self, obj):
        """Muestra el nombre del rol con colores"""
        colors = {
            'admin': '#f44336',
            'gerente': '#2196F3',
            'vendedor': '#FF9800',
            'operador': '#9C27B0'
        }
        color = colors.get(obj.rol, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_rol_display()
        )
    get_rol_display.short_description = 'Rol'
    
    def num_permisos(self, obj):
        """Muestra el número de permisos asignados"""
        count = obj.permisos.count()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            'green' if count > 0 else 'red',
            count
        )
    num_permisos.short_description = 'Permisos'
    
    def num_usuarios(self, obj):
        """Muestra el número de usuarios con este rol"""
        count = obj.get_num_usuarios()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            'blue' if count > 0 else 'gray',
            count
        )
    num_usuarios.short_description = 'Usuarios'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('permisos')


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Admin mejorado para gestionar usuarios con roles y permisos
    """
    list_display = ('username', 'email', 'get_rol_display', 'activo', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('rol', 'activo', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    filter_horizontal = ('user_permissions', 'groups')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Roles y Permisos', {
            'fields': (
                'rol',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'description': 'Configure el rol del usuario. Los permisos del rol se aplicarán automáticamente. También puede asignar permisos adicionales manualmente.'
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas Importantes', {
            'fields': ('date_joined', 'last_login', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name')
        }),
        ('Roles y Permisos', {
            'fields': (
                'rol',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'fecha_creacion', 'fecha_actualizacion')
    
    def get_rol_display(self, obj):
        """Muestra el rol del usuario con colores"""
        if obj.rol:
            colors = {
                'admin': '#f44336',
                'gerente': '#2196F3',
                'vendedor': '#FF9800',
                'operador': '#9C27B0'
            }
            color = colors.get(obj.rol, '#757575')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
                color,
                obj.get_rol_display()
            )
        return '-'
    get_rol_display.short_description = 'Rol'
    
    def save_model(self, request, obj, form, change):
        """Aplicar permisos del rol básico al guardar"""
        super().save_model(request, obj, form, change)
        
        # Si tiene un rol básico, aplicar los permisos de la configuración del rol
        if obj.rol:
            try:
                config_rol = ConfiguracionRol.objects.get(rol=obj.rol, activo=True)
                
                # Agregar permisos del rol
                for permiso in config_rol.permisos.all():
                    obj.user_permissions.add(permiso)
                
                # Agregar grupos del rol
                for grupo in config_rol.grupos.all():
                    obj.groups.add(grupo)
            except ConfiguracionRol.DoesNotExist:
                # Si no hay configuración para este rol, no hacer nada
                pass
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('user_permissions', 'groups')


# Mejorar la visualización de Permisos en el admin
class PermissionAdmin(admin.ModelAdmin):
    """Admin mejorado para gestionar permisos"""
    list_display = ('codename', 'name', 'content_type', 'get_roles_count')
    list_filter = ('content_type',)
    search_fields = ('codename', 'name', 'content_type__app_label', 'content_type__model')
    
    def get_roles_count(self, obj):
        """Muestra cuántos roles tienen este permiso"""
        count = obj.roles.count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'blue' if count > 0 else 'gray',
            count
        )
    get_roles_count.short_description = 'Roles que usan este permiso'


# Registrar el admin mejorado de permisos
# Nota: Permission no está registrado por defecto, así que lo registramos directamente
admin.site.register(Permission, PermissionAdmin)

