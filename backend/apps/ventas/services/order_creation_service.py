"""
Servicio de Creación de Órdenes desde MercadoPago
Responsabilidad: Crear órdenes e items cuando se recibe notificación de pago
"""
import logging
from decimal import Decimal
from typing import Dict, Optional, List
from django.db import transaction

from apps.ventas.models import Orden, OrdenItem, Carrito, CarritoItem, Ticket, Venta
from apps.usuarios.models import PerfilCliente
from .payment_status_mapper import PaymentStatusMapper
from .qr_service import QRCodeService

logger = logging.getLogger(__name__)


class OrderCreationService:
    """
    Servicio para crear órdenes e inscripciones/tickets desde datos del carrito
    cuando MercadoPago notifica un pago
    """
    
    @transaction.atomic
    def create_from_cart(
        self,
        carrito_data: Dict,
        payment_info: Optional[Dict] = None,
        payment_id: Optional[str] = None,
        order_status: str = 'pendiente',
        external_reference: Optional[str] = None,
        mp_status: Optional[str] = None
    ) -> Orden:
        """
        Crear orden y tickets desde datos del carrito
        
        Args:
            carrito_data: Datos del carrito con items
            payment_info: Información del pago de MP
            payment_id: ID de transacción de MP
            order_status: Estado de la orden
            external_reference: Referencia externa
            mp_status: Estado de MP
            
        Returns:
            Orden creada
        """
        order_data = self._prepare_order_data(carrito_data, payment_info)
        
        order = self._create_order(
            carrito_data=carrito_data,
            order_data=order_data,
            payment_id=payment_id,
            order_status=order_status,
            external_reference=external_reference,
            mp_status=mp_status,
            payment_info=payment_info
        )
        
        self._create_order_items(order, order_data['items'])
        
        # Solo crear tickets si el pago no está pendiente
        if order_status != 'pendiente':
            self._create_tickets(order, order_data['items'], carrito_data['cliente'])
        
        self._update_cart(
            carrito_data=carrito_data,
            payment_id=payment_id,
            order_status=order_status,
            mp_status=mp_status,
            payment_info=payment_info
        )
        
        logger.info(f"Orden {order.id} creada exitosamente con estado: {order_status}")
        
        return order
    
    def _prepare_order_data(self, carrito_data: Dict, payment_info: Optional[Dict]) -> Dict:
        """
        Preparar datos de la orden
        
        Args:
            carrito_data: Datos del carrito
            payment_info: Información del pago
            
        Returns:
            Dict con items preparados y totales
        """
        items = carrito_data.get('items', [])
        precio_original = Decimal('0.00')
        prepared = []
        
        for item in items:
            unit_price = Decimal(str(item.zona.precio))
            cantidad = item.cantidad
            
            prepared.append({
                'zona': item.zona,
                'presentacion': item.zona.presentacion,
                'unit_price': unit_price,
                'cantidad': cantidad,
            })
            
            precio_original += unit_price * cantidad
        
        # Usar monto de MercadoPago si está disponible, sino el precio original
        monto_pagado = Decimal(str(payment_info.get('transaction_amount', precio_original))) if payment_info else precio_original
        
        return {
            'items': prepared,
            'precio_original': precio_original,
            'monto_pagado': monto_pagado,
        }
    
    def _create_order(
        self,
        carrito_data: Dict,
        order_data: Dict,
        payment_id: Optional[str],
        order_status: str,
        external_reference: Optional[str],
        mp_status: Optional[str],
        payment_info: Optional[Dict]
    ) -> Orden:
        """
        Crear la orden
        
        Args:
            carrito_data: Datos del carrito
            order_data: Datos preparados de la orden
            payment_id: ID del pago
            order_status: Estado de la orden
            external_reference: Referencia externa
            mp_status: Estado de MP
            payment_info: Info del pago
            
        Returns:
            Orden creada
        """
        return Orden.objects.create(
            cliente=carrito_data['cliente'],
            total=order_data['monto_pagado'],
            mp_payment_id=payment_id,
            mp_status=mp_status,
            mp_status_detail=payment_info.get('status_detail') if payment_info else None,
            mp_payment_method_id=payment_info.get('payment_method_id') if payment_info else None,
            mp_payment_type=payment_info.get('payment_type_id') if payment_info else None,
            mp_preference_id=external_reference,
            estado=order_status,
        )
    
    def _create_order_items(self, order: Orden, items: List[Dict]) -> None:
        """
        Crear items de la orden
        
        Args:
            order: Orden creada
            items: Lista de items a crear
        """
        for item in items:
            OrdenItem.objects.create(
                orden=order,
                zona=item['zona'],
                cantidad=item['cantidad'],
                precio_unitario=item['unit_price'],
            )
    
    def _create_tickets(self, order: Orden, items: List[Dict], cliente: PerfilCliente) -> None:
        """
        Crear tickets para la orden
        
        Args:
            order: Orden creada
            items: Items de la orden
            cliente: Cliente que compra
        """
        # Primero necesitamos crear una Venta vinculada a la orden
        venta = Venta.objects.create(
            cliente_pagador=cliente,
            total_pagado=order.total,
            metodo_pago='TARJETA',  # MercadoPago usa tarjeta generalmente
            nro_operacion=order.mp_payment_id or '',
            observaciones=f'Pago procesado por MercadoPago - Orden #{order.id}',
            orden=order,
            # Nota: vendedor se deja NULL para compras online
            vendedor=None,
        )
        
        # Crear tickets por cada item
        for item in items:
            for _ in range(item['cantidad']):
                ticket = Ticket.objects.create(
                    venta=venta,
                    presentacion=item['zona'].presentacion,
                    zona=item['zona'],
                    # Titular se completa al momento de validar ingreso
                    dni_titular=None,
                    nombre_titular=None,
                )
                
                # Generar QR code
                qr_file, token = QRCodeService.generar_qr(
                    codigo_uuid=str(ticket.codigo_uuid),
                    ticket_id=ticket.id,
                    usar_encriptacion=True
                )
                
                if token:
                    ticket.token_encriptado = token
                
                ticket.qr_image.save(f'ticket_{ticket.codigo_uuid}.png', qr_file, save=True)
        
        logger.info(f"Tickets creados para orden {order.id}")
    
    def _update_cart(
        self,
        carrito_data: Dict,
        payment_id: Optional[str],
        order_status: str,
        mp_status: Optional[str],
        payment_info: Optional[Dict]
    ) -> None:
        """
        Actualizar estado del carrito
        
        Args:
            carrito_data: Datos del carrito
            payment_id: ID del pago
            order_status: Estado de la orden
            mp_status: Estado de MP
            payment_info: Info del pago
        """
        carrito_id = carrito_data.get('carrito_id')
        
        if not carrito_id or order_status not in ['pendiente', 'completado']:
            return
        
        try:
            carrito = Carrito.objects.get(id=carrito_id)
            
            # Solo marcar como inactivo si está completado
            if order_status == 'completado':
                carrito.activo = False
                carrito.save()
                
            logger.info(f"Carrito {carrito_id} actualizado")
        except Carrito.DoesNotExist:
            logger.warning(f"Carrito {carrito_id} no encontrado")
