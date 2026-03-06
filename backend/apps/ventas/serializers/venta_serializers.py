"""
Serializers para Venta
Responsabilidad: Serialización de datos de ventas
Aplicando principios SOLID
"""
from rest_framework import serializers
from apps.ventas.models import Venta, MetodoPago
from apps.usuarios.serializers import PerfilClienteSerializer
from .ticket_serializers import TicketSerializer, TicketListSerializer


class VentaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Venta con tickets
    Responsabilidad: Representación completa de venta para uso general
    """
    tickets = TicketSerializer(many=True, read_only=True)
    cliente_pagador = PerfilClienteSerializer(read_only=True)
    vendedor_nombre = serializers.CharField(source='vendedor.username', read_only=True)
    vendedor_email = serializers.EmailField(source='vendedor.email', read_only=True)
    cantidad_tickets = serializers.SerializerMethodField(read_only=True)
    tickets_activos = serializers.SerializerMethodField(read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    puede_anularse = serializers.SerializerMethodField(read_only=True)
    orden_id = serializers.IntegerField(source='orden.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Venta
        fields = [
            'id', 'codigo_venta', 'vendedor', 'vendedor_nombre', 'vendedor_email',
            'cliente_pagador', 'fecha_venta', 'total_pagado', 
            'metodo_pago', 'metodo_pago_display', 'nro_operacion',
            'observaciones', 'activo', 'orden_id', 'tickets', 
            'cantidad_tickets', 'tickets_activos', 'puede_anularse'
        ]
        read_only_fields = ['id', 'codigo_venta', 'fecha_venta']
    
    def get_cantidad_tickets(self, obj):
        """Contar cantidad total de tickets de la venta"""
        return obj.cantidad_tickets()
    
    def get_tickets_activos(self, obj):
        """Contar tickets activos de la venta"""
        return obj.tickets_activos()
    
    def get_puede_anularse(self, obj):
        """Verificar si la venta puede ser anulada"""
        return obj.puede_anularse()


class VentaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de ventas
    Responsabilidad: Representación mínima para listados eficientes
    """
    cliente_nombre = serializers.CharField(source='cliente_pagador.nombre_completo', read_only=True)
    cliente_dni = serializers.CharField(source='cliente_pagador.dni', read_only=True)
    vendedor_nombre = serializers.CharField(source='vendedor.username', read_only=True)
    cantidad_tickets = serializers.SerializerMethodField(read_only=True)
    tickets_activos = serializers.SerializerMethodField(read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'id', 'codigo_venta', 'cliente_nombre', 'cliente_dni', 'vendedor_nombre', 
            'total_pagado', 'metodo_pago', 'metodo_pago_display',
            'cantidad_tickets', 'tickets_activos', 'fecha_venta', 'activo'
        ]
        read_only_fields = fields
    
    def get_cantidad_tickets(self, obj):
        """Contar cantidad total de tickets"""
        return obj.cantidad_tickets()
    
    def get_tickets_activos(self, obj):
        """Contar tickets activos"""
        return obj.tickets_activos()


class VentaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para visualización completa de venta
    Responsabilidad: Proporcionar vista completa con toda la información relacionada
    """
    tickets = TicketSerializer(many=True, read_only=True)
    cliente_pagador = PerfilClienteSerializer(read_only=True)
    vendedor_info = serializers.SerializerMethodField(read_only=True)
    orden_info = serializers.SerializerMethodField(read_only=True)
    estadisticas = serializers.SerializerMethodField(read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    puede_anularse = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'id', 'vendedor_info', 'cliente_pagador', 'fecha_venta', 
            'total_pagado', 'metodo_pago', 'metodo_pago_display',
            'nro_operacion', 'observaciones', 'activo', 'orden_info',
            'tickets', 'estadisticas', 'puede_anularse'
        ]
        read_only_fields = fields
    
    def get_vendedor_info(self, obj):
        """Obtener información del vendedor"""
        return {
            'id': obj.vendedor.id,
            'username': obj.vendedor.username,
            'email': obj.vendedor.email,
            'rol': obj.vendedor.rol
        }
    
    def get_orden_info(self, obj):
        """Obtener información de la orden si existe"""
        if obj.orden:
            return {
                'id': obj.orden.id,
                'fecha_orden': obj.orden.fecha_orden,
                'mp_payment_id': obj.orden.mp_payment_id,
                'mp_status': obj.orden.mp_status,
                'estado': obj.orden.estado
            }
        return None
    
    def get_estadisticas(self, obj):
        """Obtener estadísticas de la venta"""
        from apps.ventas.models import EstadoTicket
        tickets = obj.tickets.all()
        
        return {
            'total_tickets': tickets.count(),
            'tickets_activos': tickets.filter(estado=EstadoTicket.ACTIVO).count(),
            'tickets_usados': tickets.filter(estado=EstadoTicket.USADO).count(),
            'tickets_anulados': tickets.filter(estado=EstadoTicket.ANULADO).count(),
        }
    
    def get_puede_anularse(self, obj):
        """Verificar si la venta puede ser anulada"""
        return obj.puede_anularse()


class VentaCreateSerializer(serializers.Serializer):
    """
    Serializer para crear una venta completa con múltiples tickets (venta manual)
    Responsabilidad: Validar datos de entrada para creación de venta manual
    Interface Segregation Principle - Solo campos necesarios para venta manual
    """
    # Datos del cliente
    cliente_dni = serializers.CharField(
        max_length=8,
        min_length=8,
        help_text="DNI del cliente que realiza el pago (8 dígitos)"
    )
    cliente_nombre = serializers.CharField(
        max_length=200,
        help_text="Nombre completo del cliente"
    )
    cliente_telefono = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True,
        help_text="Teléfono del cliente (opcional)"
    )
    cliente_email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Email del cliente (opcional)"
    )
    
    # Datos de pago
    metodo_pago = serializers.ChoiceField(
        choices=MetodoPago.choices,
        help_text="Método de pago utilizado"
    )
    nro_operacion = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Número de operación bancaria o código de transacción (opcional)"
    )
    observaciones = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Observaciones adicionales de la venta (opcional)"
    )
    
    # Tickets
    tickets = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=10,
        help_text="Lista de tickets a crear (mínimo 1, máximo 10)"
    )
    
    def validate_cliente_dni(self, value):
        """Validar formato del DNI"""
        if not value.isdigit():
            raise serializers.ValidationError("El DNI debe contener solo dígitos")
        if len(value) != 8:
            raise serializers.ValidationError("El DNI debe tener exactamente 8 dígitos")
        return value
    
    def validate_tickets(self, tickets):
        """
        Validar tickets siguiendo el flujo: Evento → Presentación → Zona
        """
        from apps.eventos.models import Zona, Presentacion
        
        for idx, ticket in enumerate(tickets, 1):
            # Validar campos requeridos
            campos_requeridos = ['presentacion_id', 'zona_id', 'dni_titular', 'nombre_titular']
            for campo in campos_requeridos:
                if campo not in ticket:
                    raise serializers.ValidationError(
                        f"Ticket #{idx}: Falta el campo '{campo}'"
                    )
            
            # Validar DNI del titular
            dni = ticket['dni_titular']
            if not isinstance(dni, str) or len(dni) != 8 or not dni.isdigit():
                raise serializers.ValidationError(
                    f"Ticket #{idx}: DNI inválido. Debe tener 8 dígitos"
                )
            
            # Validar nombre del titular
            nombre = ticket['nombre_titular']
            if not isinstance(nombre, str) or len(nombre.strip()) < 3:
                raise serializers.ValidationError(
                    f"Ticket #{idx}: Nombre debe tener al menos 3 caracteres"
                )
            
            # Validar presentación existe
            presentacion_id = ticket['presentacion_id']
            try:
                presentacion = Presentacion.objects.select_related('evento').get(id=presentacion_id)
                if not presentacion.evento.activo:
                    raise serializers.ValidationError(
                        f"Ticket #{idx}: El evento no está activo"
                    )
            except Presentacion.DoesNotExist:
                raise serializers.ValidationError(
                    f"Ticket #{idx}: La presentación no existe"
                )
            
            # Validar que la zona pertenece a la presentación seleccionada
            zona_id = ticket['zona_id']
            try:
                zona = Zona.objects.select_related('presentacion').get(id=zona_id)
                if zona.presentacion_id != presentacion_id:
                    raise serializers.ValidationError(
                        f"Ticket #{idx}: La zona no pertenece a la presentación seleccionada"
                    )
                if not zona.activo:
                    raise serializers.ValidationError(
                        f"Ticket #{idx}: La zona no está disponible"
                    )
                # Validar disponibilidad
                if not zona.tiene_disponibilidad():
                    raise serializers.ValidationError(
                        f"Ticket #{idx}: La zona '{zona.nombre}' no tiene disponibilidad"
                    )
            except Zona.DoesNotExist:
                raise serializers.ValidationError(
                    f"Ticket #{idx}: La zona no existe"
                )
        
        return tickets
    
    def validate(self, attrs):
        """
        Validar límites de tickets por titular
        """
        from apps.ventas.models import Ticket, EstadoTicket
        from apps.eventos.models import Presentacion
        
        tickets_data = attrs.get('tickets', [])
        
        # Agrupar tickets por titular y evento
        titulares_eventos = {}
        for ticket_data in tickets_data:
            dni_titular = ticket_data['dni_titular']
            presentacion_id = ticket_data['presentacion_id']
            
            # Obtener evento de la presentación
            presentacion = Presentacion.objects.select_related('evento').get(id=presentacion_id)
            evento_id = presentacion.evento_id
            
            key = f"{dni_titular}_{evento_id}"
            if key not in titulares_eventos:
                # Contar tickets existentes
                tickets_existentes = Ticket.objects.filter(
                    dni_titular=dni_titular,
                    presentacion__evento_id=evento_id,
                    estado=EstadoTicket.ACTIVO
                ).count()
                titulares_eventos[key] = {
                    'dni': dni_titular,
                    'evento_nombre': presentacion.evento.nombre,
                    'count': tickets_existentes
                }
            
            titulares_eventos[key]['count'] += 1
            
            # Validar límite de 3 tickets por titular por evento
            if titulares_eventos[key]['count'] > 3:
                raise serializers.ValidationError({
                    'tickets': f"El titular con DNI {dni_titular} excede el límite de 3 tickets "
                               f"para el evento '{titulares_eventos[key]['evento_nombre']}'"
                })
        
        return attrs


class AnularVentaSerializer(serializers.Serializer):
    """
    Serializer para anular una venta completa
    Responsabilidad: Validar datos para anulación de venta
    """
    motivo = serializers.CharField(
        max_length=500,
        help_text="Motivo de la anulación de la venta"
    )
    
    def validate_motivo(self, value):
        """Validar que se proporcione un motivo"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Debe proporcionar un motivo para anular la venta")
        return value.strip()


class VentaEstadisticasSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de ventas
    Responsabilidad: Estructurar datos de estadísticas
    """
    total_ventas = serializers.IntegerField(read_only=True)
    total_ingresos = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_tickets = serializers.IntegerField(read_only=True)
    tickets_activos = serializers.IntegerField(read_only=True)
    tickets_usados = serializers.IntegerField(read_only=True)
    tickets_anulados = serializers.IntegerField(read_only=True)
    ventas_por_metodo_pago = serializers.DictField(read_only=True)
    ventas_por_vendedor = serializers.ListField(read_only=True)

