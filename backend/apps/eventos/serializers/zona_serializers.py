"""
Serializers para Zona
Responsabilidad: Serialización de datos de zonas
"""
from rest_framework import serializers
from apps.eventos.models import Zona



class ZonaSerializer(serializers.ModelSerializer):
    """Serializer completo para Zona con campos calculados"""
    tickets_vendidos = serializers.IntegerField(read_only=True)
    tickets_disponibles = serializers.IntegerField(read_only=True)
    porcentaje_ocupacion = serializers.FloatField(read_only=True)
    capacidad = serializers.IntegerField(source='capacidad_maxima', required=False)
    
    class Meta:
        model = Zona
        fields = [
            'id', 'codigo', 'presentacion', 'nombre', 'descripcion', 'precio', 
            'capacidad', 'capacidad_maxima', 'activo', 'tickets_vendidos', 
            'tickets_disponibles', 'porcentaje_ocupacion'
        ]
        read_only_fields = ['id', 'codigo', 'tickets_vendidos', 'tickets_disponibles', 'porcentaje_ocupacion']
        extra_kwargs = {'capacidad_maxima': {'write_only': True}}
    
    def to_representation(self, instance):
        """Agregar campos calculados"""
        representation = super().to_representation(instance)
        representation['tickets_vendidos'] = instance.tickets_vendidos()
        representation['tickets_disponibles'] = instance.tickets_disponibles()
        representation['porcentaje_ocupacion'] = instance.porcentaje_ocupacion()
        return representation


class ZonaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para zonas sin información extra"""
    
    class Meta:
        model = Zona
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'precio', 'capacidad_maxima', 'activo']
        read_only_fields = ['id', 'codigo']


class ZonaDetalleSerializer(serializers.ModelSerializer):
    """Serializer para detalles de zona con disponibilidad de tickets"""
    tickets_disponibles = serializers.SerializerMethodField()
    tickets_vendidos = serializers.SerializerMethodField()
    
    class Meta:
        model = Zona
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'precio', 'capacidad_maxima', 'activo', 'tickets_disponibles', 'tickets_vendidos']
        read_only_fields = ['id', 'codigo']
    
    def get_tickets_disponibles(self, obj):
        """Obtener tickets disponibles"""
        return obj.tickets_disponibles()
    
    def get_tickets_vendidos(self, obj):
        """Obtener tickets vendidos"""
        return obj.tickets_vendidos()


class ZonaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de zonas"""
    tickets_disponibles = serializers.IntegerField(read_only=True)
    tickets_vendidos = serializers.IntegerField(read_only=True)
    capacidad = serializers.IntegerField(source='capacidad_maxima')
    evento_nombre = serializers.CharField(source='presentacion.evento.nombre', read_only=True)
    evento_lugar = serializers.CharField(source='presentacion.evento.lugar', read_only=True)
    presentacion_fecha = serializers.DateField(source='presentacion.fecha', read_only=True)
    presentacion_hora = serializers.TimeField(source='presentacion.hora_inicio', read_only=True)
    
    class Meta:
        model = Zona
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'precio', 'capacidad', 
            'tickets_disponibles', 'tickets_vendidos', 'activo', 
            'evento_nombre', 'evento_lugar', 'presentacion_fecha', 'presentacion_hora'
        ]
        read_only_fields = ['id', 'codigo']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tickets_disponibles'] = instance.tickets_disponibles()
        representation['tickets_vendidos'] = instance.tickets_vendidos()
        return representation
