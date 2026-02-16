"""
Serializers para Validaciones
Interface específica para el proceso de validación en puerta
"""
from rest_framework import serializers
from .models import Validacion
from apps.ventas.serializers import TicketValidacionSerializer


class ValidacionSerializer(serializers.ModelSerializer):
    """Serializer completo para Validación"""
    ticket = TicketValidacionSerializer(read_only=True)
    validador_nombre = serializers.CharField(source='validador.nombre_completo', read_only=True)
    
    class Meta:
        model = Validacion
        fields = ['id', 'ticket', 'validador', 'validador_nombre', 
                  'fecha_hora_ingreso', 'observaciones', 'ip_address', 'dispositivo']
        read_only_fields = ['fecha_hora_ingreso']


class ValidacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado"""
    titular_nombre = serializers.CharField(source='ticket.nombre_titular', read_only=True)
    titular_dni = serializers.CharField(source='ticket.dni_titular', read_only=True)
    validador_nombre = serializers.CharField(source='validador.nombre_completo', read_only=True)
    zona_nombre = serializers.CharField(source='ticket.zona.nombre', read_only=True)
    
    class Meta:
        model = Validacion
        fields = ['id', 'titular_nombre', 'titular_dni', 'zona_nombre', 
                  'validador_nombre', 'fecha_hora_ingreso']


class ValidarTicketSerializer(serializers.Serializer):
    """
    Serializer para validar un ticket por su código UUID
    Responsabilidad: Procesar la entrada del escáner QR
    """
    codigo_uuid = serializers.UUIDField(
        help_text="UUID del ticket escaneado desde el código QR"
    )
    observaciones = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Observaciones opcionales del validador"
    )
    ip_address = serializers.IPAddressField(required=False)
    dispositivo = serializers.CharField(max_length=200, required=False, allow_blank=True)
