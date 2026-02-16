"""
Serializers para Ventas y Tickets
Aplicando Interface Segregation
"""
from rest_framework import serializers
from .models import Venta, Ticket
from apps.usuarios.serializers import PerfilClienteSerializer
from apps.eventos.serializers import ZonaListSerializer


class TicketSerializer(serializers.ModelSerializer):
    """Serializer completo para Ticket"""
    zona = ZonaListSerializer(read_only=True)
    evento_nombre = serializers.CharField(source='zona.evento.nombre', read_only=True)
    qr_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = ['id', 'venta', 'zona', 'evento_nombre', 'dni_titular', 
                  'nombre_titular', 'codigo_uuid', 'estado', 'qr_image', 
                  'qr_image_url', 'fecha_creacion']
        read_only_fields = ['codigo_uuid', 'qr_image', 'fecha_creacion']
    
    def get_qr_image_url(self, obj):
        if obj.qr_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_image.url)
        return None


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado"""
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    evento_nombre = serializers.CharField(source='zona.evento.nombre', read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'dni_titular', 'nombre_titular', 'zona_nombre', 
                  'evento_nombre', 'estado', 'fecha_creacion']


class TicketValidacionSerializer(serializers.ModelSerializer):
    """Serializer para validación de tickets en puerta"""
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    evento_nombre = serializers.CharField(source='zona.evento.nombre', read_only=True)
    precio = serializers.DecimalField(source='zona.precio', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'dni_titular', 'nombre_titular', 'zona_nombre', 
                  'evento_nombre', 'precio', 'estado', 'codigo_uuid']


class VentaSerializer(serializers.ModelSerializer):
    """Serializer completo para Venta"""
    tickets = TicketSerializer(many=True, read_only=True)
    cliente_pagador = PerfilClienteSerializer(read_only=True)
    vendedor_nombre = serializers.CharField(source='vendedor.username', read_only=True)
    cantidad_tickets = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Venta
        fields = ['id', 'vendedor', 'vendedor_nombre', 'cliente_pagador', 
                  'fecha_venta', 'total_pagado', 'metodo_pago', 'nro_operacion',
                  'observaciones', 'tickets', 'cantidad_tickets']
        read_only_fields = ['fecha_venta']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cantidad_tickets'] = instance.cantidad_tickets()
        return representation


class VentaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de ventas"""
    cliente_nombre = serializers.CharField(source='cliente_pagador.nombre_completo', read_only=True)
    cliente_dni = serializers.CharField(source='cliente_pagador.dni', read_only=True)
    vendedor_nombre = serializers.CharField(source='vendedor.username', read_only=True)
    cantidad_tickets = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Venta
        fields = ['id', 'cliente_nombre', 'cliente_dni', 'vendedor_nombre', 'total_pagado', 
                  'metodo_pago', 'cantidad_tickets', 'fecha_venta']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cantidad_tickets'] = instance.cantidad_tickets()
        return representation


class CrearVentaSerializer(serializers.Serializer):
    """
    Serializer para crear una venta completa con múltiples tickets
    Responsabilidad: Validar datos de entrada para creación de venta
    """
    # Datos del cliente
    cliente_dni = serializers.CharField(max_length=8, min_length=8)
    cliente_nombre = serializers.CharField(max_length=200)
    cliente_telefono = serializers.CharField(max_length=15, required=False, allow_blank=True)
    cliente_email = serializers.EmailField(required=False, allow_blank=True)
    
    # Datos de pago
    metodo_pago = serializers.ChoiceField(choices=['EFECTIVO', 'TRANSFERENCIA', 'YAPE', 'PLIN', 'TARJETA'])
    nro_operacion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    
    # Tickets
    tickets = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=10,
        help_text="Lista de tickets a crear"
    )
    
    def validate_tickets(self, tickets):
        """Validar estructura de tickets"""
        for ticket in tickets:
            if 'zona_id' not in ticket:
                raise serializers.ValidationError("Cada ticket debe tener 'zona_id'")
            if 'dni_titular' not in ticket:
                raise serializers.ValidationError("Cada ticket debe tener 'dni_titular'")
            if 'nombre_titular' not in ticket:
                raise serializers.ValidationError("Cada ticket debe tener 'nombre_titular'")
            
            # Validar longitud del DNI
            if len(ticket['dni_titular']) != 8 or not ticket['dni_titular'].isdigit():
                raise serializers.ValidationError(f"DNI {ticket['dni_titular']} inválido. Debe tener 8 dígitos")
        
        return tickets
