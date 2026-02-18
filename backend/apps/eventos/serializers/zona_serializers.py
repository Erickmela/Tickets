"""
Serializers para Zona
Responsabilidad: Serialización de datos de zonas
"""
from rest_framework import serializers
from apps.eventos.models import Zona
from config.hashid_utils import encode_id


class ZonaSerializer(serializers.ModelSerializer):
    """Serializer completo para Zona con campos calculados"""
    encoded_id = serializers.SerializerMethodField()
    tickets_vendidos = serializers.IntegerField(read_only=True)
    tickets_disponibles = serializers.IntegerField(read_only=True)
    porcentaje_ocupacion = serializers.FloatField(read_only=True)
    capacidad = serializers.IntegerField(source='capacidad_maxima', required=False)
    
    class Meta:
        model = Zona
        fields = [
            'id', 'encoded_id', 'evento', 'nombre', 'descripcion', 'precio', 
            'capacidad', 'capacidad_maxima', 'activo', 'tickets_vendidos', 
            'tickets_disponibles', 'porcentaje_ocupacion'
        ]
        read_only_fields = ['tickets_vendidos', 'tickets_disponibles', 'porcentaje_ocupacion', 'encoded_id']
        extra_kwargs = {'capacidad_maxima': {'write_only': True}}
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)
    
    def to_representation(self, instance):
        """Agregar campos calculados"""
        representation = super().to_representation(instance)
        representation['tickets_vendidos'] = instance.tickets_vendidos()
        representation['tickets_disponibles'] = instance.tickets_disponibles()
        representation['porcentaje_ocupacion'] = instance.porcentaje_ocupacion()
        return representation


class ZonaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para zonas sin información extra"""
    encoded_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Zona
        fields = ['id', 'encoded_id', 'nombre', 'descripcion', 'precio', 'capacidad_maxima', 'activo']
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)


class ZonaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de zonas"""
    encoded_id = serializers.SerializerMethodField()
    tickets_disponibles = serializers.IntegerField(read_only=True)
    tickets_vendidos = serializers.IntegerField(read_only=True)
    capacidad = serializers.IntegerField(source='capacidad_maxima')
    evento_nombre = serializers.CharField(source='evento.nombre', read_only=True)
    evento_fecha = serializers.DateField(source='evento.fecha', read_only=True)
    evento_lugar = serializers.CharField(source='evento.lugar', read_only=True)
    
    class Meta:
        model = Zona
        fields = [
            'id', 'encoded_id', 'nombre', 'descripcion', 'precio', 'capacidad', 
            'tickets_disponibles', 'tickets_vendidos', 'activo', 
            'evento_nombre', 'evento_fecha', 'evento_lugar'
        ]
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tickets_disponibles'] = instance.tickets_disponibles()
        representation['tickets_vendidos'] = instance.tickets_vendidos()
        return representation
