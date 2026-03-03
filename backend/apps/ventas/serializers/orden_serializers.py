"""
Serializers para Orden y OrdenItem
Responsabilidad: Serialización de datos de órdenes (futuro MercadoPago)
"""
from rest_framework import serializers
from apps.ventas.models import Orden, OrdenItem
from apps.usuarios.serializers import PerfilClienteSerializer
from apps.eventos.serializers import ZonaSimpleSerializer


class OrdenItemSerializer(serializers.ModelSerializer):
    """
    Serializer completo para OrdenItem
    Responsabilidad: Representación completa de un item de orden con información de zona
    """
    zona = ZonaSimpleSerializer(read_only=True)
    zona_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = OrdenItem
        fields = [
            'id', 'orden', 'zona', 'zona_id', 'cantidad', 
            'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['id', 'subtotal']
    
    def get_subtotal(self, obj):
        """Calcular subtotal del item"""
        return obj.cantidad * obj.precio_unitario


class OrdenItemSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para OrdenItem
    Responsabilidad: Representación mínima de item de orden
    """
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = OrdenItem
        fields = ['id', 'zona_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['id', 'subtotal']
    
    def get_subtotal(self, obj):
        """Calcular subtotal del item"""
        return obj.cantidad * obj.precio_unitario


class OrdenSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Orden
    Responsabilidad: Representación completa de orden con items y cliente
    """
    items = OrdenItemSerializer(many=True, read_only=True)
    cliente = PerfilClienteSerializer(read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cantidad_items = serializers.SerializerMethodField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Orden
        fields = [
            'id', 'cliente', 'cliente_nombre', 'fecha_orden', 'total', 
            'mp_payment_id', 'mp_status', 'mp_status_detail', 
            'mp_payment_method_id', 'mp_payment_type', 'mp_preference_id',
            'mp_merchant_order_id', 'estado', 'estado_display', 'observaciones',
            'items', 'cantidad_items'
        ]
        read_only_fields = [
            'id', 'fecha_orden', 'mp_payment_id', 'mp_status', 
            'mp_status_detail', 'mp_payment_method_id', 'mp_payment_type',
            'mp_preference_id', 'mp_merchant_order_id'
        ]
    
    def get_cantidad_items(self, obj):
        """Contar cantidad total de items en la orden"""
        return obj.items.count()


class OrdenListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de órdenes
    Responsabilidad: Representación mínima para listados eficientes
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_dni = serializers.CharField(source='cliente.dni', read_only=True)
    cantidad_items = serializers.SerializerMethodField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Orden
        fields = [
            'id', 'cliente_nombre', 'cliente_dni', 'fecha_orden', 
            'total', 'estado', 'estado_display', 'mp_payment_id', 
            'mp_status', 'cantidad_items'
        ]
        read_only_fields = fields
    
    def get_cantidad_items(self, obj):
        """Contar cantidad total de items en la orden"""
        return obj.items.count()


class OrdenCreateSerializer(serializers.Serializer):
    """
    Serializer para crear órdenes desde MercadoPago
    Responsabilidad: Validar y estructurar datos de entrada para crear orden
    Open/Closed Principle - Extensible para futuros métodos de pago
    """
    cliente_id = serializers.IntegerField(
        help_text="ID del perfil de cliente que realiza la orden"
    )
    
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=20,
        help_text="Lista de items a incluir en la orden"
    )
    
    mp_preference_id = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="ID de preferencia de MercadoPago"
    )
    
    observaciones = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Observaciones adicionales de la orden"
    )
    
    def validate_items(self, items):
        """
        Validar estructura y datos de items
        Responsabilidad: Asegurar integridad de datos de items
        """
        from apps.eventos.models import Zona
        
        for item in items:
            # Validar campos requeridos
            if 'zona_id' not in item:
                raise serializers.ValidationError("Cada item debe tener 'zona_id'")
            if 'cantidad' not in item:
                raise serializers.ValidationError("Cada item debe tener 'cantidad'")
            
            # Validar que la cantidad sea positiva
            cantidad = item.get('cantidad', 0)
            if not isinstance(cantidad, int) or cantidad <= 0:
                raise serializers.ValidationError(
                    f"La cantidad debe ser un número entero positivo"
                )
            
            # Validar que la cantidad no exceda el límite razonable
            if cantidad > 10:
                raise serializers.ValidationError(
                    f"No se pueden agregar más de 10 tickets de una misma zona por orden"
                )
            
            # Validar que la zona existe y está activa
            zona_id = item['zona_id']
            try:
                zona = Zona.objects.select_related('presentacion__evento').get(id=zona_id)
                if not zona.activo:
                    raise serializers.ValidationError(
                        f"La zona '{zona.nombre}' no está disponible para la venta"
                    )
                if not zona.presentacion.evento.activo:
                    raise serializers.ValidationError(
                        f"El evento '{zona.presentacion.evento.nombre}' no está disponible para la venta"
                    )
                # Validar disponibilidad
                if zona.tickets_disponibles() < cantidad:
                    raise serializers.ValidationError(
                        f"La zona '{zona.nombre}' no tiene suficientes tickets disponibles. "
                        f"Disponibles: {zona.tickets_disponibles()}, solicitados: {cantidad}"
                    )
            except Zona.DoesNotExist:
                raise serializers.ValidationError(f"La zona con ID {zona_id} no existe")
        
        return items
    
    def validate_cliente_id(self, value):
        """
        Validar que el cliente existe
        Responsabilidad: Verificar existencia del cliente
        """
        from apps.usuarios.models import PerfilCliente
        
        try:
            PerfilCliente.objects.get(id=value)
        except PerfilCliente.DoesNotExist:
            raise serializers.ValidationError(f"El cliente con ID {value} no existe")
        
        return value


class OrdenDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para visualización completa de orden
    Responsabilidad: Proporcionar vista completa con toda la información relacionada
    """
    items = OrdenItemSerializer(many=True, read_only=True)
    cliente = PerfilClienteSerializer(read_only=True)
    ventas = serializers.SerializerMethodField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Orden
        fields = [
            'id', 'cliente', 'fecha_orden', 'total', 'estado', 'estado_display',
            'mp_payment_id', 'mp_status', 'mp_status_detail', 
            'mp_payment_method_id', 'mp_payment_type', 'mp_preference_id',
            'mp_merchant_order_id', 'observaciones', 'items', 'ventas'
        ]
        read_only_fields = fields
    
    def get_ventas(self, obj):
        """Obtener información de ventas asociadas a esta orden"""
        ventas = obj.ventas.all()
        return [{
            'id': venta.id,
            'fecha_venta': venta.fecha_venta,
            'total_pagado': venta.total_pagado,
            'metodo_pago': venta.metodo_pago,
            'cantidad_tickets': venta.cantidad_tickets()
        } for venta in ventas]
