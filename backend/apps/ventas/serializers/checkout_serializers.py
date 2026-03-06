"""
Serializers para Checkout
Responsabilidad: Validar datos para compras desde el carrito
"""
from rest_framework import serializers
from apps.ventas.models import MetodoPago, Orden, OrdenItem
from apps.eventos.models import Zona, Presentacion


class CheckoutItemSerializer(serializers.Serializer):
    """
    Serializer para cada item del carrito en el checkout
    """
    presentacion_id = serializers.IntegerField(help_text="ID de la presentación")
    zona_id = serializers.IntegerField(help_text="ID de la zona")
    cantidad = serializers.IntegerField(min_value=1, max_value=10, help_text="Cantidad de tickets para esta zona")
    
    def validate(self, data):
        """Validar que la zona pertenece a la presentación"""
        presentacion_id = data['presentacion_id']
        zona_id = data['zona_id']
        
        try:
            presentacion = Presentacion.objects.get(id=presentacion_id)
        except Presentacion.DoesNotExist:
            raise serializers.ValidationError("La presentación no existe")
        
        try:
            zona = Zona.objects.get(id=zona_id)
        except Zona.DoesNotExist:
            raise serializers.ValidationError("La zona no existe")
        
        if zona.presentacion_id != presentacion_id:
            raise serializers.ValidationError(
                f"La zona '{zona.nombre}' no pertenece a la presentación seleccionada"
            )
        
        if not zona.activo:
            raise serializers.ValidationError(f"La zona '{zona.nombre}' no está activa")
        
        # Validar disponibilidad
        if not zona.tiene_disponibilidad(data['cantidad']):
            disponibles = zona.tickets_disponibles()
            raise serializers.ValidationError(
                f"La zona '{zona.nombre}' solo tiene {disponibles} tickets disponibles. " 
                f"Solicitaste {data['cantidad']}."
            )
        
        data['zona'] = zona
        data['presentacion'] = presentacion
        return data


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer para procesar el checkout desde el carrito
    
    El usuario ya está autenticado, así que no necesitamos sus datos.
    Solo necesitamos el método de pago y los items del carrito.
    """
    metodo_pago = serializers.ChoiceField(
        choices=MetodoPago.choices,
        help_text="Método de pago a utilizar"
    )
    nro_operacion = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Número de operación para Yape, Plin, transferencia, etc."
    )
    observaciones = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Observaciones adicionales"
    )
    items = serializers.ListField(
        child=CheckoutItemSerializer(),
        min_length=1,
        help_text="Items del carrito a procesar"
    )
    
    def validate_items(self, items):
        """Validar límite de tickets totales por compra"""
        total_tickets = sum(item['cantidad'] for item in items)
        
        if total_tickets > 10:
            raise serializers.ValidationError(
                f"No puedes comprar más de 10 tickets en una sola compra. "
                f"Seleccionaste {total_tickets} tickets."
            )
        
        return items
    
    def validate(self, data):
        """Validaciones globales"""
        # Validar que el usuario no exceda el límite de 3 tickets por evento
        items = data['items']
        
        # Agrupar por evento para validar límite
        eventos_tickets = {}
        for item in items:
            evento_id = item['presentacion'].evento.id
            if evento_id not in eventos_tickets:
                eventos_tickets[evento_id] = 0
            eventos_tickets[evento_id] += item['cantidad']
        
        # Verificar límite por evento
        for evento_id, cantidad in eventos_tickets.items():
            if cantidad > 3:
                from apps.eventos.models import Evento
                evento = Evento.objects.get(id=evento_id)
                raise serializers.ValidationError(
                    f"No puedes comprar más de 3 tickets para el evento '{evento.nombre}'. "
                    f"Seleccionaste {cantidad} tickets."
                )
        
        return data
