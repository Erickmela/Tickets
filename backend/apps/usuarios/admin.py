from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, PerfilCliente


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'get_nombre_completo', 'email', 'rol', 'is_active')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'perfil_cliente__nombre_completo')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('email',)}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser')}),
        ('Fechas', {'fields': ('last_login', 'fecha_creacion')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'rol', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'last_login')
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del perfil cliente"""
        if hasattr(obj, 'perfil_cliente') and obj.perfil_cliente:
            return obj.perfil_cliente.nombre_completo
        return '-'
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(PerfilCliente)
class PerfilClienteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombre_completo', 'telefono', 'get_email', 'fecha_registro')
    search_fields = ('dni', 'nombre_completo', 'telefono', 'usuario__email')
    list_filter = ('fecha_registro',)
    ordering = ('-fecha_registro',)
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    
    def get_email(self, obj):
        """Obtener email del usuario vinculado"""
        if obj.usuario:
            return obj.usuario.email
        return '-'
    get_email.short_description = 'Email'
