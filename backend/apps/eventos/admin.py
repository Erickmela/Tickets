from django.contrib import admin
from .models import Evento, Zona


class ZonaInline(admin.TabularInline):
    model = Zona
    extra = 1
    fields = ('nombre', 'precio', 'capacidad_maxima', 'activo')


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'activo', 'total_zonas', 'tickets_vendidos', 'capacidad_total')
    list_filter = ('activo', 'fecha')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha',)
    inlines = [ZonaInline]
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('nombre', 'descripcion', 'fecha', 'hora_inicio', 'lugar')
        }),
        ('Imágenes Promocionales', {
            'fields': ('imagen_principal', 'imagen_flyer', 'imagen_banner', 'imagen_cartel'),
            'description': 'Imágenes para promocionar el evento'
        }),
        ('Información del Recinto', {
            'fields': ('imagen_mapa_zonas',),
            'description': 'Mapa/plano con la distribución de zonas del local para que los clientes vean dónde compran'
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ('evento', 'nombre', 'precio', 'tickets_vendidos', 'capacidad_maxima', 'porcentaje_ocupacion', 'activo')
    list_filter = ('evento', 'activo')
    search_fields = ('nombre', 'evento__nombre')
    ordering = ('evento', 'precio')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'tickets_vendidos', 'tickets_disponibles')
    
    fieldsets = (
        ('Evento y Zona', {
            'fields': ('evento', 'nombre', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('precio', 'capacidad_maxima', 'activo')
        }),
        ('Estadísticas', {
            'fields': ('tickets_vendidos', 'tickets_disponibles'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
