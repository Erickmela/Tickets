"""
Serializers para Eventos y Zonas
Aplicando principios de serialización limpia
"""
from rest_framework import serializers
from .models import Evento, Zona
from config.hashid_utils import encode_id

class ZonaSerializer(serializers.ModelSerializer):
    """Serializer para Zona"""
    encoded_id = serializers.SerializerMethodField()
    tickets_vendidos = serializers.IntegerField(read_only=True)
    tickets_disponibles = serializers.IntegerField(read_only=True)
    porcentaje_ocupacion = serializers.FloatField(read_only=True)
    capacidad = serializers.IntegerField(source='capacidad_maxima', required=False)
    
    class Meta:
        model = Zona
        fields = ['id', 'encoded_id', 'evento', 'nombre', 'descripcion', 'precio', 
                  'capacidad', 'capacidad_maxima', 'activo', 'tickets_vendidos', 
                  'tickets_disponibles', 'porcentaje_ocupacion']
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
        fields = ['id', 'encoded_id', 'nombre', 'descripcion', 'precio', 'capacidad', 'tickets_disponibles', 
                  'tickets_vendidos', 'activo', 'evento_nombre', 'evento_fecha', 'evento_lugar']
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tickets_disponibles'] = instance.tickets_disponibles()
        representation['tickets_vendidos'] = instance.tickets_vendidos()
        return representation


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
        fields = ['id', 'encoded_id', 'nombre', 'descripcion', 'categoria', 'fecha', 'hora_inicio',
                  'lugar', 'region', 'estado', 'activo', 'imagen_principal', 'imagen_flyer',
                  'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas', 'zonas', 'total_zonas', 'capacidad_total', 
                  'tickets_vendidos', 'disponibilidad', 'fecha_creacion']
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
        fields = ['id', 'encoded_id', 'nombre', 'descripcion', 'categoria', 'fecha', 'hora_inicio', 'lugar', 'region', 'estado', 'activo',
                  'imagen_principal', 'imagen_flyer', 'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas',
                  'total_zonas', 'capacidad_total', 'tickets_vendidos']
    
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
    """Serializer para crear eventos"""
    zonas_data = serializers.JSONField(write_only=True, required=False)
    
    class Meta:
        model = Evento
        fields = ['nombre', 'descripcion', 'categoria', 'fecha', 'hora_inicio', 'lugar', 'region', 'estado', 'activo',
                  'imagen_principal', 'imagen_flyer', 'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas',
                  'zonas_data']
    
    def validate_hora_inicio(self, value):
        """Validar que hora_inicio no sea un string vacío"""
        if value == '' or value is None:
            return None
        return value
    
    def create(self, validated_data):
        """Crear evento con sus zonas"""
        import json
        from decimal import Decimal, InvalidOperation
        
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
                # Convertir string a tipos numéricos
                try:
                    precio = Decimal(str(zona_info.get('precio', 0)))
                except (InvalidOperation, ValueError, TypeError):
                    precio = Decimal('0')
                
                try:
                    capacidad = int(zona_info.get('capacidad_maxima', 0))
                except (ValueError, TypeError):
                    capacidad = 0
                
                Zona.objects.create(
                    evento=evento,
                    nombre=zona_info.get('nombre', ''),
                    descripcion=zona_info.get('descripcion', ''),
                    precio=precio,
                    capacidad_maxima=capacidad,
                    activo=zona_info.get('activo', True)
                )
        
        return evento
    
    def update(self, instance, validated_data):
        """Actualizar evento y sus zonas"""
        import json
        from decimal import Decimal, InvalidOperation
        
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
            # Obtener IDs de zonas existentes
            zonas_existentes_ids = set()
            
            for zona_info in zonas_data:
                zona_id = zona_info.get('id')
                
                # Convertir string a tipos numéricos
                try:
                    precio = Decimal(str(zona_info.get('precio', 0)))
                except (InvalidOperation, ValueError, TypeError):
                    precio = Decimal('0')
                
                try:
                    capacidad = int(zona_info.get('capacidad_maxima', 0))
                except (ValueError, TypeError):
                    capacidad = 0
                
                if zona_id:
                    # Actualizar zona existente
                    try:
                        zona = Zona.objects.get(id=zona_id, evento=instance)
                        zona.nombre = zona_info.get('nombre', zona.nombre)
                        zona.descripcion = zona_info.get('descripcion', zona.descripcion)
                        zona.precio = precio
                        zona.capacidad_maxima = capacidad
                        zona.activo = zona_info.get('activo', zona.activo)
                        zona.save()
                        zonas_existentes_ids.add(zona_id)
                    except Zona.DoesNotExist:
                        pass
                else:
                    # Crear nueva zona
                    nueva_zona = Zona.objects.create(
                        evento=instance,
                        nombre=zona_info.get('nombre', ''),
                        descripcion=zona_info.get('descripcion', ''),
                        precio=precio,
                        capacidad_maxima=capacidad,
                        activo=zona_info.get('activo', True)
                    )
                    zonas_existentes_ids.add(nueva_zona.id)
            
            # Eliminar zonas que ya no están en la lista
            # (Comentado para no eliminar zonas con tickets vendidos)
            # instance.zonas.exclude(id__in=zonas_existentes_ids).delete()
        
        return instance
