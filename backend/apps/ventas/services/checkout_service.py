"""
Servicio de Checkout
Responsabilidad: Procesar compras desde el carrito del cliente
"""
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.ventas.models import Orden, OrdenItem, Venta, Ticket, MetodoPago, EstadoTicket
from apps.usuarios.models import PerfilCliente
from .qr_service import QRCodeService


class CheckoutService:
    """
    Servicio para procesar checkout desde el carrito
    Responsabilidad: Coordinar la creación de orden, venta y tickets desde el carrito
    """
    
    @staticmethod
    @transaction.atomic
    def procesar_checkout(cliente: PerfilCliente, datos_checkout: dict) -> dict:
        """
        Procesa el checkout completo:
        1. Crea la Orden con los items
        2. Crea la Venta vinculada
        3. Crea los Tickets (sin titular asignado)
        4. Genera QR codes
        
        Returns:
            dict con orden_id, venta_id, tickets_ids, total
        """
        items_data = datos_checkout['items']
        
        # Paso 1: Calcular total
        total = CheckoutService._calcular_total(items_data)
        
        # Paso 2: Crear orden
        orden = Orden.objects.create(
            cliente=cliente,
            total=total,
            estado='pendiente'
        )
        
        # Paso 3: Crear items de la orden
        CheckoutService._crear_orden_items(orden, items_data)
        
        # Paso 4: Crear venta vinculada (sin vendedor, es compra online)
        venta = CheckoutService._crear_venta(
            orden=orden,
            cliente=cliente,
            metodo_pago=datos_checkout['metodo_pago'],
            nro_operacion=datos_checkout.get('nro_operacion', ''),
            observaciones=datos_checkout.get('observaciones', '')
        )
        
        # Paso 5: Crear tickets (sin titular asignado)
        tickets = CheckoutService._crear_tickets(venta, items_data)
        
        # Paso 6: Actualizar estado de orden
        orden.estado = 'completada'
        orden.save()
        
        return {
            'orden_id': orden.id,
            'venta_id': venta.id,
            'tickets': [
                {
                    'id': ticket.id,
                    'codigo_uuid': str(ticket.codigo_uuid),
                    'zona': ticket.zona.nombre,
                    'precio': float(ticket.zona.precio),
                    'qr_url': ticket.qr_image.url if ticket.qr_image else None
                }
                for ticket in tickets
            ],
            'total': float(total),
            'cantidad_tickets': len(tickets)
        }
    
    @staticmethod
    def _calcular_total(items_data: list) -> Decimal:
        """Calcular el total de la compra"""
        total = Decimal('0.00')
        for item in items_data:
            zona = item['zona']
            cantidad = item['cantidad']
            total += Decimal(str(zona.precio)) * cantidad
        return total
    
    @staticmethod
    def _crear_orden_items(orden: Orden, items_data: list):
        """Crear los items de la orden"""
        for item in items_data:
            OrdenItem.objects.create(
                orden=orden,
                zona=item['zona'],
                cantidad=item['cantidad'],
                precio_unitario=item['zona'].precio
            )
    
    @staticmethod
    def _crear_venta(orden: Orden, cliente: PerfilCliente, metodo_pago: str, 
                     nro_operacion: str, observaciones: str) -> Venta:
        """
        Crear venta vinculada a la orden
        Para compras online, el vendedor puede ser None o un usuario del sistema
        """
        # Buscar un usuario del sistema para asignar como vendedor
        # O dejarlo None si tu modelo lo permite
        from apps.usuarios.models import Usuario
        vendedor_sistema = Usuario.objects.filter(
            rol='VENDEDOR',
            is_active=True
        ).first()
        
        if not vendedor_sistema:
            # Si no hay vendedor del sistema, crear uno automático
            # O simplemente usar el primer admin
            vendedor_sistema = Usuario.objects.filter(
                is_superuser=True,
                is_active=True
            ).first()
        
        venta = Venta.objects.create(
            vendedor=vendedor_sistema,
            cliente_pagador=cliente,
            total_pagado=orden.total,
            metodo_pago=metodo_pago,
            nro_operacion=nro_operacion,
            observaciones=observaciones or f'Compra online - Orden #{orden.id}',
            orden=orden
        )
        
        return venta
    
    @staticmethod
    def _crear_tickets(venta: Venta, items_data: list) -> list:
        """
        Crear tickets sin titular asignado
        El titular se asignará al momento de validar el ingreso al evento
        """
        tickets = []
        
        for item in items_data:
            zona = item['zona']
            presentacion = item['presentacion']
            cantidad = item['cantidad']
            
            for i in range(cantidad):
                # Crear ticket sin titular
                ticket = Ticket.objects.create(
                    venta=venta,
                    presentacion=presentacion,
                    zona=zona,
                    dni_titular=None,  # Se completa al ingresar al evento
                    nombre_titular=None,  # Se completa al ingresar al evento
                    estado=EstadoTicket.ACTIVO
                )
                
                # Generar QR code
                try:
                    QRCodeService.generar_qr_para_ticket(ticket)
                except Exception as e:
                    print(f"Error generando QR para ticket {ticket.id}: {e}")
                
                tickets.append(ticket)
        
        return tickets
    
    @staticmethod
    def validar_disponibilidad(items_data: list) -> dict:
        """
        Validar disponibilidad en tiempo real antes del checkout
        Returns: dict con status y mensaje
        """
        for item in items_data:
            zona = item['zona']
            cantidad = item['cantidad']
            
            if not zona.tiene_disponibilidad(cantidad):
                disponibles = zona.tickets_disponibles()
                return {
                    'disponible': False,
                    'mensaje': f"La zona '{zona.nombre}' solo tiene {disponibles} tickets disponibles. "
                              f"Solicitaste {cantidad}."
                }
        
        return {
            'disponible': True,
            'mensaje': 'Todos los tickets están disponibles'
        }
