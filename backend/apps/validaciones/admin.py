from django.contrib import admin
from .models import Validacion


@admin.register(Validacion)
class ValidacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'validador', 'fecha_hora_ingreso', 'get_titular', 'get_zona')
    list_filter = ('fecha_hora_ingreso', 'validador', 'ticket__zona__evento')
    search_fields = ('ticket__dni_titular', 'ticket__nombre_titular', 'ticket__codigo_uuid')
    ordering = ('-fecha_hora_ingreso',)
    readonly_fields = ('ticket', 'validador', 'fecha_hora_ingreso', 'ip_address', 'dispositivo')
    
    fieldsets = (
        ('Información de Validación', {
            'fields': ('ticket', 'validador', 'fecha_hora_ingreso')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'ip_address', 'dispositivo'),
            'classes': ('collapse',)
        }),
    )
    
    def get_titular(self, obj):
        return obj.ticket.nombre_titular
    get_titular.short_description = 'Titular'
    
    def get_zona(self, obj):
        return obj.ticket.zona.nombre
    get_zona.short_description = 'Zona'
    
    def has_add_permission(self, request):
        """No permitir añadir validaciones manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar validaciones (auditoría)"""
        return False
