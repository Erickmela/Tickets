"""
Serializers para Ticket
Responsabilidad: Serialización de datos de tickets
"""
from rest_framework import serializers
from apps.ventas.models import Ticket
from apps.eventos.serializers import ZonaSimpleSerializer


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Ticket con información de zona, evento y presentación
    Responsabilidad: Representación completa del ticket para uso general
    """
    zona = ZonaSimpleSerializer(read_only=True)
    zona_id = serializers.IntegerField(write_only=True, required=False)
    evento_nombre = serializers.CharField(source='zona.presentacion.evento.nombre', read_only=True)
    presentacion_fecha = serializers.DateField(source='presentacion.fecha', read_only=True)
    presentacion_hora = serializers.TimeField(source='presentacion.hora_inicio', read_only=True)
    precio = serializers.DecimalField(
        source='zona.precio',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    qr_image_url = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    puede_usarse = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'venta', 'presentacion', 'zona', 'zona_id', 'evento_nombre',
            'presentacion_fecha', 'presentacion_hora', 'dni_titular', 
            'nombre_titular', 'codigo_uuid', 'estado', 'estado_display',
            'precio', 'qr_image', 'qr_image_url', 'puede_usarse',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'id', 'codigo_uuid', 'qr_image', 'fecha_creacion', 
            'fecha_actualizacion', 'token_encriptado'
        ]
    
    def get_qr_image_url(self, obj):
        """Generar URL absoluta para la imagen del QR"""
        if obj.qr_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_image.url)
        return None
    
    def get_puede_usarse(self, obj):
        """Verificar si el ticket puede ser usado"""
        return obj.puede_usarse()


class TicketListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de tickets
    Responsabilidad: Representación mínima para listados eficientes
    """
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    evento_nombre = serializers.CharField(source='zona.presentacion.evento.nombre', read_only=True)
    presentacion_fecha = serializers.DateField(source='presentacion.fecha', read_only=True)
    presentacion_hora = serializers.TimeField(source='presentacion.hora_inicio', read_only=True)
    precio = serializers.DecimalField(
        source='zona.precio',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'dni_titular', 'nombre_titular', 'zona_nombre', 
            'evento_nombre', 'presentacion_fecha', 'presentacion_hora',
            'precio', 'estado', 'estado_display', 'fecha_creacion'
        ]
        read_only_fields = fields


class TicketDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para visualización completa de ticket
    Responsabilidad: Proporcionar vista completa con toda la información
    """
    zona = ZonaSimpleSerializer(read_only=True)
    venta_info = serializers.SerializerMethodField(read_only=True)
    evento_info = serializers.SerializerMethodField(read_only=True)
    presentacion_info = serializers.SerializerMethodField(read_only=True)
    qr_image_url = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    puede_usarse = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'venta', 'venta_info', 'presentacion', 'presentacion_info',
            'zona', 'evento_info', 'dni_titular', 'nombre_titular', 
            'codigo_uuid', 'estado', 'estado_display', 'qr_image', 
            'qr_image_url', 'puede_usarse', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = fields
    
    def get_qr_image_url(self, obj):
        """Generar URL absoluta para la imagen del QR"""
        if obj.qr_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_image.url)
        return None
    
    def get_puede_usarse(self, obj):
        """Verificar si el ticket puede ser usado"""
        return obj.puede_usarse()
    
    def get_venta_info(self, obj):
        """Obtener información resumida de la venta"""
        venta = obj.venta
        return {
            'id': venta.id,
            'fecha_venta': venta.fecha_venta,
            'total_pagado': venta.total_pagado,
            'metodo_pago': venta.metodo_pago,
            'vendedor': venta.vendedor.username,
            'cliente': venta.cliente_pagador.nombre_completo
        }
    
    def get_evento_info(self, obj):
        """Obtener información del evento"""
        evento = obj.zona.presentacion.evento
        return {
            'id': evento.id,
            'nombre': evento.nombre,
            'lugar': evento.lugar,
            'region': evento.region
        }
    
    def get_presentacion_info(self, obj):
        """Obtener información de la presentación"""
        if obj.presentacion:
            return {
                'id': obj.presentacion.id,
                'fecha': obj.presentacion.fecha,
                'hora_inicio': obj.presentacion.hora_inicio,
                'descripcion': obj.presentacion.descripcion
            }
        return None


class TicketValidacionSerializer(serializers.ModelSerializer):
    """
    Serializer para validación de tickets en puerta
    Responsabilidad: Proporcionar información necesaria para validación en el acceso
    """
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    evento_nombre = serializers.CharField(source='zona.presentacion.evento.nombre', read_only=True)
    presentacion_fecha = serializers.DateField(source='presentacion.fecha', read_only=True)
    presentacion_hora = serializers.TimeField(source='presentacion.hora_inicio', read_only=True)
    precio = serializers.DecimalField(
        source='zona.precio', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    puede_usarse = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'dni_titular', 'nombre_titular', 'zona_nombre', 
            'evento_nombre', 'presentacion_fecha',
            'presentacion_hora', 'precio', 'estado', 'estado_display',
            'codigo_uuid', 'puede_usarse', 'fecha_creacion'
        ]
        read_only_fields = fields
    
    def get_puede_usarse(self, obj):
        """Verificar si el ticket puede ser usado"""
        return obj.puede_usarse()


class MarcarTicketUsadoSerializer(serializers.Serializer):
    """
    Serializer para marcar un ticket como usado
    Responsabilidad: Validar datos para marcar ticket usado
    """
    codigo_uuid = serializers.UUIDField(
        help_text="Código UUID del ticket a validar"
    )
    
    token_encriptado = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Token encriptado del QR (opcional, para validación avanzada)"
    )
    
    validador_observacion = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Observaciones del validador (opcional)"
    )


class AnularTicketSerializer(serializers.Serializer):
    """
    Serializer para anular un ticket
    Responsabilidad: Validar datos para anulación de ticket
    """
    motivo = serializers.CharField(
        max_length=500,
        help_text="Motivo de la anulación del ticket"
    )
    
    def validate_motivo(self, value):
        """Validar que se proporcione un motivo"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Debe proporcionar un motivo para anular el ticket")
        return value.strip()
