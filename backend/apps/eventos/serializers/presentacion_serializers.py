"""
Serializers para Presentacion
Responsabilidad: Serialización de datos de presentaciones
"""
from rest_framework import serializers
from apps.eventos.models import Presentacion


class PresentacionSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Presentacion
    Responsabilidad: Representación completa de una presentación
    """
    evento_nombre = serializers.CharField(source='evento.nombre', read_only=True)
    fecha_hora_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Presentacion
        fields = [
            'id', 'evento', 'evento_nombre', 'fecha', 'hora_inicio', 
            'descripcion', 'fecha_hora_display'
        ]
        read_only_fields = ['id']
    
    def get_fecha_hora_display(self, obj):
        """Formato legible de fecha y hora"""
        return f"{obj.fecha.strftime('%d/%m/%Y')} - {obj.hora_inicio.strftime('%H:%M')}"


class PresentacionSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para Presentacion con sus zonas
    Responsabilidad: Representación mínima para uso en otros serializers
    """
    fecha_hora_display = serializers.SerializerMethodField(read_only=True)
    zonas = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Presentacion
        fields = ['id', 'fecha', 'hora_inicio', 'descripcion', 'fecha_hora_display', 'zonas']
        read_only_fields = fields
    
    def get_fecha_hora_display(self, obj):
        """Formato legible de fecha y hora"""
        return f"{obj.fecha.strftime('%d/%m/%Y')} - {obj.hora_inicio.strftime('%H:%M')}"
    
    def get_zonas(self, obj):
        """Obtener las zonas de esta presentación con información de disponibilidad"""
        from .zona_serializers import ZonaDetalleSerializer
        zonas = obj.zonas.filter(activo=True)
        return ZonaDetalleSerializer(zonas, many=True).data


class PresentacionListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de presentaciones
    Responsabilidad: Representación para listados eficientes
    """
    evento_nombre = serializers.CharField(source='evento.nombre', read_only=True)
    evento_lugar = serializers.CharField(source='evento.lugar', read_only=True)
    fecha_hora_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Presentacion
        fields = [
            'id', 'evento_nombre', 'evento_lugar', 'fecha', 
            'hora_inicio', 'descripcion', 'fecha_hora_display'
        ]
        read_only_fields = fields
    
    def get_fecha_hora_display(self, obj):
        """Formato legible de fecha y hora"""
        return f"{obj.fecha.strftime('%d/%m/%Y')} - {obj.hora_inicio.strftime('%H:%M')}"


class PresentacionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear presentaciones
    Responsabilidad: Validar datos de entrada para creación
    """
    class Meta:
        model = Presentacion
        fields = ['evento', 'fecha', 'hora_inicio', 'descripcion']
    
    def validate(self, attrs):
        """Validar que no exista una presentación duplicada"""
        evento = attrs.get('evento')
        fecha = attrs.get('fecha')
        hora_inicio = attrs.get('hora_inicio')
        
        # Verificar si ya existe una presentación con la misma fecha y hora
        if Presentacion.objects.filter(
            evento=evento,
            fecha=fecha,
            hora_inicio=hora_inicio
        ).exists():
            raise serializers.ValidationError(
                "Ya existe una presentación para este evento en la misma fecha y hora"
            )
        
        return attrs
