"""
Serializers para Evento
Responsabilidad: Serialización de datos de eventos
"""
import json
from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from apps.eventos.models import Evento, Zona, Presentacion, Categoria
from config.hashid_utils import encode_id
from .zona_serializers import ZonaSimpleSerializer
from .presentacion_serializers import PresentacionSimpleSerializer


class EventoSerializer(serializers.ModelSerializer):
    """Serializer completo para Evento con zonas y presentaciones"""
    encoded_id = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    zonas = ZonaSimpleSerializer(many=True, read_only=True)
    presentaciones = PresentacionSimpleSerializer(many=True, read_only=True)
    total_zonas = serializers.IntegerField(read_only=True)
    capacidad_total = serializers.IntegerField(read_only=True)
    tickets_vendidos = serializers.IntegerField(read_only=True)
    disponibilidad = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Evento
        fields = [
            'id', 'encoded_id', 'nombre', 'descripcion', 'categoria', 'categoria_nombre',
            'lugar', 'region', 'estado', 'activo', 'comision_porcentaje', 'comision_incluida_precio',
            'imagen_principal', 'imagen_flyer', 'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas',
            'zonas', 'presentaciones', 'total_zonas', 'capacidad_total', 'tickets_vendidos',
            'disponibilidad', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion', 'encoded_id', 'categoria_nombre']
    
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
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    total_zonas = serializers.IntegerField(read_only=True)
    capacidad_total = serializers.IntegerField(read_only=True)
    tickets_vendidos = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Evento
        fields = [
            'id', 'encoded_id', 'nombre', 'descripcion', 'categoria', 'categoria_nombre',
            'lugar', 'region', 'estado', 'activo', 'comision_porcentaje', 'comision_incluida_precio',
            'imagen_principal', 'imagen_flyer', 'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas',
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


class EventoLandingSerializer(serializers.ModelSerializer):
    """
    Serializer ultra-ligero para landing page
    Solo campos esenciales para mostrar tarjetas de eventos
    """
    encoded_id = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    fecha = serializers.SerializerMethodField()
    precio_desde = serializers.SerializerMethodField()
    
    class Meta:
        model = Evento
        fields = [
            'id', 'encoded_id', 'nombre', 'categoria_nombre',
            'lugar', 'region', 'estado', 'activo', 'imagen_principal',
            'fecha', 'precio_desde'
        ]
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)
    
    def get_fecha(self, obj):
        """Obtener fecha de la primera presentación"""
        primera_presentacion = obj.presentaciones.order_by('fecha').first()
        if primera_presentacion:
            return primera_presentacion.fecha.isoformat()
        return None
    
    def get_precio_desde(self, obj):
        """Obtener el precio mínimo de todas las zonas del evento"""
        precio_min = None
        for presentacion in obj.presentaciones.all():
            zonas = presentacion.zonas.filter(activo=True)
            if zonas.exists():
                zona_min = zonas.order_by('precio').first()
                if zona_min:
                    if precio_min is None or zona_min.precio < precio_min:
                        precio_min = zona_min.precio
        
        return float(precio_min) if precio_min else None


class EventoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar eventos con presentaciones y zonas"""
    presentaciones_data = serializers.JSONField(write_only=True, required=False, help_text='Array de presentaciones con fecha, hora y zonas')
    # Campos retrocompatibles (deprecated - usar presentaciones_data)
    fecha = serializers.DateField(write_only=True, required=False, help_text='[DEPRECATED] Usar presentaciones_data')
    hora_inicio = serializers.TimeField(write_only=True, required=False, help_text='[DEPRECATED] Usar presentaciones_data')
    zonas_data = serializers.JSONField(write_only=True, required=False, help_text='[DEPRECATED] Usar presentaciones_data')
    
    class Meta:
        model = Evento
        fields = [
            'nombre', 'descripcion', 'categoria', 'lugar', 
            'region', 'estado', 'activo', 'comision_porcentaje', 'comision_incluida_precio',
            'imagen_principal', 'imagen_flyer', 'imagen_banner', 'imagen_cartel', 'imagen_mapa_zonas', 
            'presentaciones_data', 'fecha', 'hora_inicio', 'zonas_data'
        ]
    
    def create(self, validated_data):
        """
        Crear evento con múltiples presentaciones y sus zonas
        
        presentaciones_data formato esperado:
        [
            {
                "fecha": "2026-03-15",
                "hora_inicio": "20:00",
                "descripcion": "Noche 1",
                "zonas": [
                    {"nombre": "VIP", "precio": 150.00, "capacidad_maxima": 100},
                    {"nombre": "GENERAL", "precio": 80.00, "capacidad_maxima": 500}
                ]
            },
            {
                "fecha": "2026-03-16",
                "hora_inicio": "20:00",
                "descripcion": "Noche 2",
                "zonas": [...]
            }
        ]
        """
        # Extraer presentaciones_data
        presentaciones_data = validated_data.pop('presentaciones_data', None)
        if isinstance(presentaciones_data, str):
            try:
                presentaciones_data = json.loads(presentaciones_data)
            except json.JSONDecodeError:
                presentaciones_data = None
        
        # Retrocompatibilidad: si no hay presentaciones_data, usar fecha/hora_inicio/zonas_data antiguos
        if not presentaciones_data:
            fecha = validated_data.pop('fecha', None)
            hora_inicio = validated_data.pop('hora_inicio', None)
            zonas_data = validated_data.pop('zonas_data', None)
            
            if isinstance(zonas_data, str):
                try:
                    zonas_data = json.loads(zonas_data)
                except json.JSONDecodeError:
                    zonas_data = None
            
            # Crear array de presentaciones en formato nuevo
            if fecha and hora_inicio:
                presentaciones_data = [{
                    'fecha': fecha.isoformat() if hasattr(fecha, 'isoformat') else str(fecha),
                    'hora_inicio': hora_inicio.isoformat() if hasattr(hora_inicio, 'isoformat') else str(hora_inicio),
                    'descripcion': 'Presentación principal',
                    'zonas': zonas_data or []
                }]
        else:
            # Limpiar campos deprecated si vienen
            validated_data.pop('fecha', None)
            validated_data.pop('hora_inicio', None)
            validated_data.pop('zonas_data', None)
        
        # Crear el evento
        evento = Evento.objects.create(**validated_data)
        
        # Crear presentaciones con sus zonas
        if presentaciones_data and isinstance(presentaciones_data, list):
            for present_info in presentaciones_data:
                self._crear_presentacion_con_zonas(evento, present_info)
        
        return evento
    
    def update(self, instance, validated_data):
        """Actualizar evento y sus zonas"""
        # Extraer datos de presentación (no se actualizan por este serializer)
        validated_data.pop('fecha', None)
        validated_data.pop('hora_inicio', None)
        
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
        # NOTA: Las zonas ahora están vinculadas a presentaciones, no a eventos
        # Para actualizar zonas, se debe usar el endpoint de presentaciones
        if zonas_data and isinstance(zonas_data, list):
            # Obtener la primera presentación del evento
            presentacion = instance.presentaciones.first()
            
            if presentacion:
                zonas_existentes_ids = set()
                
                for zona_info in zonas_data:
                    zona_id = zona_info.get('id')
                    
                    if zona_id:
                        # Actualizar zona existente
                        zona_actualizada = self._actualizar_zona(presentacion, zona_id, zona_info)
                        if zona_actualizada:
                            zonas_existentes_ids.add(zona_id)
                    else:
                        # Crear nueva zona
                        nueva_zona = self._crear_zona(presentacion, zona_info)
                        zonas_existentes_ids.add(nueva_zona.id)
        
        return instance
    
    def _crear_presentacion_con_zonas(self, evento, present_info):
        """Método auxiliar para crear una presentación con sus zonas"""
        from datetime import datetime, date, time
        
        # Extraer datos de la presentación
        fecha_str = present_info.get('fecha')
        hora_str = present_info.get('hora_inicio')
        descripcion = present_info.get('descripcion', '')
        zonas = present_info.get('zonas', [])
        
        # Convertir fecha si es string
        if isinstance(fecha_str, str):
            try:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_obj = date.today()
        else:
            fecha_obj = fecha_str
        
        # Convertir hora si es string
        if isinstance(hora_str, str):
            try:
                hora_obj = datetime.strptime(hora_str, '%H:%M:%S').time()
            except ValueError:
                try:
                    hora_obj = datetime.strptime(hora_str, '%H:%M').time()
                except ValueError:
                    hora_obj = time(20, 0)  # Default 20:00
        else:
            hora_obj = hora_str
        
        # Crear la presentación
        presentacion = Presentacion.objects.create(
            evento=evento,
            fecha=fecha_obj,
            hora_inicio=hora_obj,
            descripcion=descripcion
        )
        
        # Crear las zonas de esta presentación
        if zonas and isinstance(zonas, list):
            for zona_info in zonas:
                self._crear_zona(presentacion, zona_info)
        
        return presentacion
    
    def _crear_zona(self, presentacion, zona_info):
        """Método auxiliar para crear una zona vinculada a una presentación"""
        precio = self._parse_decimal(zona_info.get('precio', 0))
        capacidad = self._parse_int(zona_info.get('capacidad_maxima', 0))
        
        return Zona.objects.create(
            presentacion=presentacion,
            nombre=zona_info.get('nombre', ''),
            descripcion=zona_info.get('descripcion', ''),
            precio=precio,
            capacidad_maxima=capacidad,
            activo=zona_info.get('activo', True)
        )
    
    def _actualizar_zona(self, presentacion, zona_id, zona_info):
        """Método auxiliar para actualizar una zona existente"""
        try:
            zona = Zona.objects.get(id=zona_id, presentacion=presentacion)
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
