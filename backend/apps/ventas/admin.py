from django.contrib import admin
from .models import Venta, Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ('codigo_uuid', 'qr_image', 'estado', 'fecha_creacion')
    fields = ('dni_titular', 'nombre_titular', 'zona', 'codigo_uuid', 'estado', 'qr_image')
    can_delete = False


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_pagador', 'vendedor', 'total_pagado', 'metodo_pago', 'cantidad_tickets', 'fecha_venta')
    list_filter = ('metodo_pago', 'fecha_venta', 'vendedor')
    search_fields = ('cliente_pagador__nombre_completo', 'cliente_pagador__dni', 'nro_operacion')
    ordering = ('-fecha_venta',)
    inlines = [TicketInline]
    readonly_fields = ('fecha_venta',)
    
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('vendedor', 'cliente_pagador', 'fecha_venta')
        }),
        ('Pago', {
            'fields': ('total_pagado', 'metodo_pago', 'nro_operacion')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'activo'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_titular', 'dni_titular', 'zona', 'estado', 'codigo_uuid', 'fecha_creacion')
    list_filter = ('estado', 'zona__presentacion__evento', 'zona__presentacion', 'zona', 'fecha_creacion')
    search_fields = ('dni_titular', 'nombre_titular', 'codigo_uuid')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('codigo_uuid', 'qr_image', 'fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('venta', 'zona', 'estado')
        }),
        ('Titular', {
            'fields': ('dni_titular', 'nombre_titular')
        }),
        ('Seguridad', {
            'fields': ('codigo_uuid', 'qr_image')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['anular_tickets']
    
    def anular_tickets(self, request, queryset):
        """Acción para anular tickets seleccionados"""
        tickets_anulados = 0
        for ticket in queryset:
            try:
                ticket.anular('Anulado desde el admin')
                tickets_anulados += 1
            except Exception as e:
                self.message_user(request, f'Error al anular ticket {ticket.id}: {str(e)}', level='error')
        
        if tickets_anulados > 0:
            self.message_user(request, f'Se anularon {tickets_anulados} tickets correctamente')
    
    anular_tickets.short_description = 'Anular tickets seleccionados'
