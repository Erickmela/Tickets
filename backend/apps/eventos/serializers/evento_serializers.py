"""
Serializers para Evento
Responsabilidad: Serialización de datos de eventos
"""
import json
from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from apps.eventos.models import Evento, Zona
from config.hashid_utils import encode_id
from .zona_serializers import ZonaSimpleSerializer


class EventoSerializer(serializers.ModelSerializer):
    """Serializer completo para Evento con zonas"""
    encoded_id = serializers.SerializerMethodField()
    zonas = ZonaSimpleSerializer(many=True, read_only=True)
    total_zonas = serializers.IntegerField(read_only=True)
    capacidad_total = serializers.IntegerField(read_only=True)
    tickets_vendidos = serializers.IntegerField(read_only=True)
    disponibilidad = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Evento
        fields = [
            'id', 'encoded_id', 'nombre', 'descripcion', 'categoria', 'fecha', 'hora_inicio',
            'lugar', 'region', 'estado', 'activo', 'imagen_principal', 'imagen_flyer',
            'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas', 'zonas', 'total_zonas', 
            'capacidad_total', 'tickets_vendidos', 'disponibilidad', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion', 'encoded_id']
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)
    
    def to_representation(self, instance):
        """Agregar campos calculados"""
        representation = super().to_representation(instance)
        representation['total_zonas'] = instance.total_zonas()
        representation['capacidad_total'] = instance.capacidad_total()
        representation['tickets_vendidos'] = instance.tickets_vendidos()
        representation['disponibilidad'] = instance.disponibilidad()
        return representation


class EventoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de eventos"""
    encoded_id = serializers.SerializerMethodField()
    total_zonas = serializers.IntegerField(read_only=True)
    capacidad_total = serializers.IntegerField(read_only=True)
    tickets_vendidos = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Evento
        fields = [
            'id', 'encoded_id', 'nombre', 'descripcion', 'categoria', 'fecha', 'hora_inicio', 
            'lugar', 'region', 'estado', 'activo', 'imagen_principal', 'imagen_flyer', 
            'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas',
            'total_zonas', 'capacidad_total', 'tickets_vendidos'
        ]
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_zonas'] = instance.total_zonas()
        representation['capacidad_total'] = instance.capacidad_total()
        representation['tickets_vendidos'] = instance.tickets_vendidos()
        return representation


class EventoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar eventos con zonas"""
    zonas_data = serializers.JSONField(write_only=True, required=False)
    
    class Meta:
        model = Evento
        fields = [
            'nombre', 'descripcion', 'categoria', 'fecha', 'hora_inicio', 'lugar', 
            'region', 'estado', 'activo', 'imagen_principal', 'imagen_flyer', 
            'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas', 'zonas_data'
        ]
    
    def validate_hora_inicio(self, value):
        """Validar que hora_inicio no sea un string vacío"""
        if value == '' or value is None:
            return None
        return value
    
    def create(self, validated_data):
        """Crear evento con sus zonas"""
        # Extraer zonas_data si viene como string JSON
        zonas_data = validated_data.pop('zonas_data', None)
        if isinstance(zonas_data, str):
            try:
                zonas_data = json.loads(zonas_data)
            except json.JSONDecodeError:
                zonas_data = None
        
        # Crear el evento
        evento = Evento.objects.create(**validated_data)
        
        # Crear las zonas si existen
        if zonas_data and isinstance(zonas_data, list):
            for zona_info in zonas_data:
                self._crear_zona(evento, zona_info)
        
        return evento
    
    def update(self, instance, validated_data):
        """Actualizar evento y sus zonas"""
        # Extraer zonas_data si viene como string JSON
        zonas_data = validated_data.pop('zonas_data', None)
        if isinstance(zonas_data, str):
            try:
                zonas_data = json.loads(zonas_data)
            except json.JSONDecodeError:
                zonas_data = None
        
        # Actualizar campos del evento
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar zonas si existen
        if zonas_data and isinstance(zonas_data, list):
            zonas_existentes_ids = set()
            
            for zona_info in zonas_data:
                zona_id = zona_info.get('id')
                
                if zona_id:
                    # Actualizar zona existente
                    zona_actualizada = self._actualizar_zona(instance, zona_id, zona_info)
                    if zona_actualizada:
                        zonas_existentes_ids.add(zona_id)
                else:
                    # Crear nueva zona
                    nueva_zona = self._crear_zona(instance, zona_info)
                    zonas_existentes_ids.add(nueva_zona.id)
            
            # Nota: No eliminamos zonas para evitar problemas con tickets vendidos
        
        return instance
    
    def _crear_zona(self, evento, zona_info):
        """Método auxiliar para crear una zona"""
        precio = self._parse_decimal(zona_info.get('precio', 0))
        capacidad = self._parse_int(zona_info.get('capacidad_maxima', 0))
        
        return Zona.objects.create(
            evento=evento,
            nombre=zona_info.get('nombre', ''),
            descripcion=zona_info.get('descripcion', ''),
            precio=precio,
            capacidad_maxima=capacidad,
            activo=zona_info.get('activo', True)
        )
    
    def _actualizar_zona(self, evento, zona_id, zona_info):
        """Método auxiliar para actualizar una zona existente"""
        try:
            zona = Zona.objects.get(id=zona_id, evento=evento)
            zona.nombre = zona_info.get('nombre', zona.nombre)
            zona.descripcion = zona_info.get('descripcion', zona.descripcion)
            zona.precio = self._parse_decimal(zona_info.get('precio', zona.precio))
            zona.capacidad_maxima = self._parse_int(zona_info.get('capacidad_maxima', zona.capacidad_maxima))
            zona.activo = zona_info.get('activo', zona.activo)
            zona.save()
            return zona
        except Zona.DoesNotExist:
            return None
    
    @staticmethod
    def _parse_decimal(value):
        """Convertir valor a Decimal de forma segura"""
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal('0')
    
    @staticmethod
    def _parse_int(value):
        """Convertir valor a int de forma segura"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
