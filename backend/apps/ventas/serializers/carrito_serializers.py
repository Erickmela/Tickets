"""
Serializers para Carrito y CarritoItem
Responsabilidad: Serialización de datos de carritos de compra
"""
from rest_framework import serializers
from apps.ventas.models import Carrito, CarritoItem
from apps.usuarios.serializers import PerfilClienteSerializer
from apps.eventos.serializers import ZonaSimpleSerializer


class CarritoItemSerializer(serializers.ModelSerializer):
    """
    Serializer completo para CarritoItem
    Responsabilidad: Representación completa de un item del carrito con información de zona
    """
    zona = ZonaSimpleSerializer(read_only=True)
    zona_id = serializers.IntegerField(write_only=True)
    precio_unitario = serializers.DecimalField(
        source='zona.precio',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField(read_only=True)
    tickets_disponibles = serializers.SerializerMethodField(read_only=True)
    evento_nombre = serializers.CharField(source='zona.presentacion.evento.nombre', read_only=True)
    
    class Meta:
        model = CarritoItem
        fields = [
            'id', 'carrito', 'zona', 'zona_id', 'cantidad', 
            'precio_unitario', 'subtotal', 'tickets_disponibles',
            'evento_nombre'
        ]
        read_only_fields = ['id', 'carrito']
    
    def get_subtotal(self, obj):
        """Calcular subtotal del item"""
        return obj.cantidad * obj.zona.precio
    
    def get_tickets_disponibles(self, obj):
        """Obtener cantidad de tickets disponibles en la zona"""
        return obj.zona.tickets_disponibles()
    
    def validate_cantidad(self, value):
        """Validar cantidad de tickets"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        if value > 10:
            raise serializers.ValidationError("No se pueden agregar más de 10 tickets por zona")
        return value
    
    def validate_zona_id(self, value):
        """Validar que la zona existe y está activa"""
        from apps.eventos.models import Zona
        
        try:
            zona = Zona.objects.select_related('presentacion__evento').get(id=value)
            if not zona.activo:
                raise serializers.ValidationError("Esta zona no está disponible para la venta")
            if not zona.presentacion.evento.activo:
                raise serializers.ValidationError("Este evento no está disponible para la venta")
        except Zona.DoesNotExist:
            raise serializers.ValidationError("La zona especificada no existe")
        
        return value


class CarritoItemSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para CarritoItem
    Responsabilidad: Representación mínima de item del carrito
    """
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    precio_unitario = serializers.DecimalField(
        source='zona.precio',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CarritoItem
        fields = ['id', 'zona_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = fields
    
    def get_subtotal(self, obj):
        """Calcular subtotal del item"""
        return obj.cantidad * obj.zona.precio


class CarritoSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Carrito
    Responsabilidad: Representación completa del carrito con items y totales
    """
    items = CarritoItemSerializer(many=True, read_only=True)
    cliente = PerfilClienteSerializer(read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    cantidad_items = serializers.SerializerMethodField(read_only=True)
    cantidad_tickets = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Carrito
        fields = [
            'id', 'cliente', 'cliente_nombre', 'creado', 'actualizado',
            'activo', 'items', 'total', 'cantidad_items', 'cantidad_tickets'
        ]
        read_only_fields = ['id', 'creado', 'actualizado']
    
    def get_total(self, obj):
        """Calcular total del carrito"""
        return sum(item.cantidad * item.zona.precio for item in obj.items.all())
    
    def get_cantidad_items(self, obj):
        """Contar cantidad de items diferentes en el carrito"""
        return obj.items.count()
    
    def get_cantidad_tickets(self, obj):
        """Contar cantidad total de tickets en el carrito"""
        return sum(item.cantidad for item in obj.items.all())


class CarritoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de carritos
    Responsabilidad: Representación mínima para listados eficientes
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_dni = serializers.CharField(source='cliente.dni', read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    cantidad_items = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Carrito
        fields = [
            'id', 'cliente_nombre', 'cliente_dni', 'creado', 
            'actualizado', 'activo', 'total', 'cantidad_items'
        ]
        read_only_fields = fields
    
    def get_total(self, obj):
        """Calcular total del carrito"""
        return sum(item.cantidad * item.zona.precio for item in obj.items.all())
    
    def get_cantidad_items(self, obj):
        """Contar cantidad de items en el carrito"""
        return obj.items.count()


class AgregarItemCarritoSerializer(serializers.Serializer):
    """
    Serializer para agregar items al carrito
    Responsabilidad: Validar datos de entrada para agregar items
    """
    zona_id = serializers.IntegerField(
        help_text="ID de la zona para la cual se desea comprar tickets"
    )
    
    cantidad = serializers.IntegerField(
        min_value=1,
        max_value=10,
        default=1,
        help_text="Cantidad de tickets a agregar (máximo 10 por zona)"
    )
    
    def validate_zona_id(self, value):
        """Validar que la zona existe y está disponible"""
        from apps.eventos.models import Zona
        
        try:
            zona = Zona.objects.select_related('presentacion__evento').get(id=value)
            if not zona.activo:
                raise serializers.ValidationError(
                    f"La zona '{zona.nombre}' no está disponible para la venta"
                )
            if not zona.presentacion.evento.activo:
                raise serializers.ValidationError(
                    f"El evento '{zona.presentacion.evento.nombre}' no está disponible para la venta"
                )
        except Zona.DoesNotExist:
            raise serializers.ValidationError(f"La zona con ID {value} no existe")
        
        return value
    
    def validate(self, attrs):
        """Validar disponibilidad de tickets"""
        from apps.eventos.models import Zona
        
        zona_id = attrs.get('zona_id')
        cantidad = attrs.get('cantidad', 1)
        
        zona = Zona.objects.get(id=zona_id)
        disponibles = zona.tickets_disponibles()
        
        if disponibles < cantidad:
            raise serializers.ValidationError({
                'cantidad': f"Solo hay {disponibles} tickets disponibles en la zona '{zona.nombre}'"
            })
        
        return attrs


class ActualizarItemCarritoSerializer(serializers.Serializer):
    """
    Serializer para actualizar cantidad de un item del carrito
    Responsabilidad: Validar actualización de cantidad
    """
    cantidad = serializers.IntegerField(
        min_value=1,
        max_value=10,
        help_text="Nueva cantidad de tickets (máximo 10)"
    )
    
    def validate_cantidad(self, value):
        """Validar que la nueva cantidad sea válida y haya disponibilidad"""
        # La validación de disponibilidad se hará en el service/view
        # para tener acceso al CarritoItem actual
        return value


class LimpiarCarritoSerializer(serializers.Serializer):
    """
    Serializer para confirmar limpieza del carrito
    Responsabilidad: Proporcionar confirmación de acción
    """
    confirmar = serializers.BooleanField(
        default=False,
        help_text="Debe ser True para confirmar la eliminación de todos los items"
    )
    
    def validate_confirmar(self, value):
        """Validar que se confirme la acción"""
        if not value:
            raise serializers.ValidationError("Debe confirmar la eliminación de todos los items del carrito")
        return value
