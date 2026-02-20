from django.contrib import admin
from .models import Evento, Zona, Categoria, Presentacion



class ZonaInline(admin.TabularInline):
    model = Zona
    extra = 1
    fields = ('nombre', 'precio', 'capacidad_maxima', 'activo')

class PresentacionInline(admin.TabularInline):
    model = Presentacion
    extra = 1
    fields = ('fecha', 'hora_inicio', 'descripcion')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'activo')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'activo', 'total_presentaciones', 'total_zonas')
    list_filter = ('activo', 'categoria')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)
    inlines = [PresentacionInline]
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información del Evento', {
            'fields': ('nombre', 'descripcion', 'categoria', 'lugar', 'region')
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

@admin.register(Presentacion)
class PresentacionAdmin(admin.ModelAdmin):
    list_display = ('evento', 'fecha', 'hora_inicio', 'descripcion')
    list_filter = ('evento', 'fecha')
    search_fields = ('evento__nombre', 'descripcion')
    ordering = ('-fecha', 'hora_inicio')
    inlines = [ZonaInline]

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ('presentacion', 'nombre', 'precio', 'tickets_vendidos', 'capacidad_maxima', 'porcentaje_ocupacion', 'activo')
    list_filter = ('presentacion', 'activo')
    search_fields = ('nombre', 'presentacion__evento__nombre')
    ordering = ('presentacion', 'precio')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'tickets_vendidos', 'tickets_disponibles')
    fieldsets = (
        ('Presentación y Zona', {
            'fields': ('presentacion', 'nombre', 'descripcion')
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
