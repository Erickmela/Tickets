"""
Serializers para Ticket
Responsabilidad: Serialización de datos de tickets
"""
from rest_framework import serializers
from apps.ventas.models import Ticket
from apps.eventos.serializers import ZonaListSerializer


class TicketSerializer(serializers.ModelSerializer):
    """Serializer completo para Ticket con información de zona y evento"""
    zona = ZonaListSerializer(read_only=True)
    evento_nombre = serializers.CharField(source='zona.evento.nombre', read_only=True)
    qr_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'venta', 'zona', 'evento_nombre', 'dni_titular', 
            'nombre_titular', 'codigo_uuid', 'estado', 'qr_image', 
            'qr_image_url', 'fecha_creacion'
        ]
        read_only_fields = ['codigo_uuid', 'qr_image', 'fecha_creacion']
    
    def get_qr_image_url(self, obj):
        """Generar URL absoluta para la imagen del QR"""
        if obj.qr_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_image.url)
        return None


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de tickets"""
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    evento_nombre = serializers.CharField(source='zona.evento.nombre', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'dni_titular', 'nombre_titular', 'zona_nombre', 
            'evento_nombre', 'estado', 'fecha_creacion'
        ]


class TicketValidacionSerializer(serializers.ModelSerializer):
    """Serializer para validación de tickets en puerta"""
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    evento_nombre = serializers.CharField(source='zona.evento.nombre', read_only=True)
    precio = serializers.DecimalField(
        source='zona.precio', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'dni_titular', 'nombre_titular', 'zona_nombre', 
            'evento_nombre', 'precio', 'estado', 'codigo_uuid'
        ]
