"""
Servicio Principal de Webhooks de MercadoPago
Responsabilidad: Procesar notificaciones de pago de MP y actualizar órdenes
"""
import logging
from typing import Dict, Optional
from django.db import transaction

from apps.ventas.models import Orden, Carrito, CarritoItem, Ticket, Venta, EstadoTicket
from .payment_status_mapper import PaymentStatusMapper
from .order_creation_service import OrderCreationService
from .cart_reconciliation_service import CartReconciliationService

logger = logging.getLogger(__name__)


class MercadoPagoWebhookService:
    """
    Servicio para procesar notificaciones de webhook de MercadoPago
    Maneja el ciclo completo de actualización de órdenes según estado del pago
    """
    
    def __init__(self):
        self.order_creator = OrderCreationService()
        self.cart_reconciler = CartReconciliationService()
    
    def process_webhook(self, webhook_data: Dict, payment: Dict) -> None:
        """
        Procesar la notificación de webhook de MercadoPago
        
        Args:
            webhook_data: Datos del webhook
            payment: Datos del pago desde MP API
        """
        payment_id = payment.get('id')
        mp_status = payment.get('status')
        mp_status_detail = payment.get('status_detail')
        external_reference = payment.get('external_reference')
        
        # Buscar o crear la orden
        order = self._find_or_create_order(payment, webhook_data)
        
        if not order:
            logger.warning(f"No se procesó orden para paymentId: {payment_id}")
            return
        
        with transaction.atomic():
            previous_status = order.estado
            
            # Siempre actualizar la orden con los datos del pago
            self._update_order(order, payment)
            
            # Manejar el estado específico del pago solo si cambió
            if previous_status != order.estado:
                self._handle_payment_status(order, mp_status, mp_status_detail, payment)
    
    def _find_or_create_order(self, payment: Dict, webhook_data: Dict) -> Optional[Orden]:
        """
        Buscar orden existente o crearla si es necesario
        
        Args:
            payment: Datos del pago
            webhook_data: Datos del webhook
            
        Returns:
            Orden encontrada o creada, o None si no aplica
        """
        payment_id = payment.get('id')
        external_reference = payment.get('external_reference')
        mp_status = payment.get('status')
        
        # Buscar por payment_id
        try:
            order = Orden.objects.get(mp_payment_id=payment_id)
            return order
        except Orden.DoesNotExist:
            pass
        
        # Buscar por external_reference (preference_id)
        if external_reference:
            try:
                order = Orden.objects.get(mp_preference_id=external_reference)
                return order
            except Orden.DoesNotExist:
                pass
        
        # Crear orden desde carrito si es necesario
        if self._should_create_order_from_cart(external_reference, mp_status):
            order = self._create_order_from_cart(external_reference, payment)
            return order
        
        # Manejar pagos rechazados sin orden
        if self._is_rejected_payment(mp_status):
            self._handle_rejected_payment_without_order(external_reference, payment)
        
        return None
    
    def _update_order(self, order: Orden, payment: Dict) -> None:
        """
        Actualizar la orden con los datos del pago
        
        Args:
            order: Orden a actualizar
            payment: Datos del pago de MP
        """
        mp_status = payment.get('status')
        new_status = PaymentStatusMapper.map_to_order_status(
            mp_status,
            payment.get('status_detail')
        )
        
        # Actualizar payment_id si no está asignado
        if not order.mp_payment_id:
            order.mp_payment_id = payment.get('id')
        
        # Actualizar campos del pago
        if payment.get('transaction_amount'):
            order.total = payment['transaction_amount']
        
        order.mp_payment_method_id = payment.get('payment_method_id', order.mp_payment_method_id)
        order.mp_payment_type = payment.get('payment_type_id', order.mp_payment_type)
        order.mp_status_detail = payment.get('status_detail', order.mp_status_detail)
        order.mp_status = mp_status
        order.estado = new_status
        
        order.save()
        
        logger.info(f"Orden {order.id} actualizada a estado: {new_status}")
    
    def _handle_payment_status(
        self,
        order: Orden,
        mp_status: str,
        mp_status_detail: Optional[str],
        payment: Dict
    ) -> None:
        """
        Manejar el estado del pago usando estrategia
        
        Args:
            order: Orden a procesar
            mp_status: Estado de MP
            mp_status_detail: Detalle del estado
            payment: Datos del pago
        """
        handlers = {
            'approved': self._handle_approved_payment,
            'pending': self._handle_pending_payment,
            'in_process': self._handle_pending_payment,
            'rejected': self._handle_rejected_payment,
            'cancelled': self._handle_cancelled_or_expired_payment,
            'expired': self._handle_cancelled_or_expired_payment,
            'refunded': self._handle_refunded_payment,
            'charged_back': self._handle_refunded_payment,
        }
        
        handler = handlers.get(mp_status)
        if handler:
            handler(order, payment)
        else:
            logger.warning(f"Estado de pago no manejado: {mp_status} para orden {order.id}")
    
    def _handle_approved_payment(self, order: Orden, payment: Dict) -> None:
        """Manejar pago aprobado"""
        # Crear tickets si no existen
        self._create_missing_tickets(order)
        
        logger.info(f"Pago aprobado procesado para orden {order.id}")
    
    def _handle_pending_payment(self, order: Orden, payment: Dict) -> None:
        """Manejar pago pendiente"""
        logger.info(f"Pago pendiente para orden {order.id}")
    
    def _handle_rejected_payment(self, order: Orden, payment: Dict) -> None:
        """Manejar pago rechazado"""
        # Reconciliar carritos duplicados si existe relación con carrito
        # (en este modelo simplificado, asumimos que la orden ya fue creada)
        logger.info(f"Pago rechazado para orden {order.id}")
    
    def _handle_cancelled_or_expired_payment(self, order: Orden, payment: Dict) -> None:
        """Manejar pago cancelado o expirado"""
        # Anular tickets asociados
        Ticket.objects.filter(
            venta__orden=order
        ).update(estado=EstadoTicket.ANULADO)
        
        logger.info(f"Pago cancelado/expirado para orden {order.id}")
    
    def _handle_refunded_payment(self, order: Orden, payment: Dict) -> None:
        """Manejar reembolso"""
        # Anular tickets asociados
        Ticket.objects.filter(
            venta__orden=order
        ).update(estado=EstadoTicket.ANULADO)
        
        logger.info(f"Reembolso procesado para orden {order.id}")
    
    def _create_missing_tickets(self, order: Orden) -> None:
        """
        Crear tickets faltantes para una orden aprobada
        VALIDACIÓN DE CAPACIDAD CON LOCK para prevenir sobreventa
        
        Args:
            order: Orden aprobada
        """
        from apps.eventos.models import Zona
        
        items = order.items.all()
        
        # Verificar si ya tiene venta asociada
        try:
            venta = Venta.objects.get(orden=order)
        except Venta.DoesNotExist:
            # Crear venta si no existe
            venta = Venta.objects.create(
                cliente_pagador=order.cliente,
                total_pagado=order.total,
                metodo_pago='TARJETA',
                nro_operacion=order.mp_payment_id or '',
                observaciones=f'Pago aprobado por MercadoPago - Orden #{order.id}',
                orden=order,
                vendedor=None,
            )
        
        # Verificar disponibilidad y límites con LOCK de base de datos
        zonas_sin_capacidad = []
        
        with transaction.atomic():
            # Validar límites de compra
            eventos_tickets = {}
            total_tickets = 0
            
            for item in items:
                evento_id = item.zona.presentacion.evento.id
                if evento_id not in eventos_tickets:
                    eventos_tickets[evento_id] = 0
                eventos_tickets[evento_id] += item.cantidad
                total_tickets += item.cantidad
            
            # Verificar límite por evento (3 tickets)
            for evento_id, cantidad in eventos_tickets.items():
                if cantidad > 3:
                    order.estado = 'error'
                    order.observaciones = f'ERROR: Límite de 3 tickets por evento excedido ({cantidad} tickets).'
                    order.save()
                    logger.error(f"LÍMITE EXCEDIDO: Orden {order.id} tiene {cantidad} tickets (máximo 3)")
                    return
            
            # Verificar límite total (10 tickets)
            if total_tickets > 10:
                order.estado = 'error'
                order.observaciones = f'ERROR: Límite total de 10 tickets excedido ({total_tickets} tickets).'
                order.save()
                logger.error(f"LÍMITE EXCEDIDO: Orden {order.id} tiene {total_tickets} tickets (máximo 10)")
                return
            
            for item in items:
                # Lock pesimista: bloquea la zona durante la transacción
                zona_locked = Zona.objects.select_for_update().get(id=item.zona.id)
                
                existing_tickets = Ticket.objects.filter(
                    venta=venta,
                    zona=zona_locked
                ).count()
                
                tickets_needed = item.cantidad - existing_tickets
                
                if tickets_needed > 0:
                    # Verificar disponibilidad en tiempo real con la zona bloqueada
                    if not zona_locked.tiene_disponibilidad(tickets_needed):
                        disponibles = zona_locked.tickets_disponibles()
                        zonas_sin_capacidad.append({
                            'zona': zona_locked.nombre,
                            'necesarios': tickets_needed,
                            'disponibles': disponibles
                        })
            
            # Si no hay capacidad suficiente, marcar orden como problemática
            # NOTA: La orden ya existe (creada al crear preferencia de pago)
            # Solo podemos marcar error y proceder con reembolso
            if zonas_sin_capacidad:
                order.estado = 'error'
                order.observaciones = f'ERROR: Capacidad excedida. Pago aprobado pero sin stock: {zonas_sin_capacidad}'
                order.save()
                # TODO: Enviar email urgente al admin
                # TODO: Enviar email al cliente explicando que recibirá reembolso
                return
            
            # Crear tickets dentro del lock
            from .qr_service import QRCodeService
            
            for item in items:
                zona_locked = Zona.objects.select_for_update().get(id=item.zona.id)
                
                existing_tickets = Ticket.objects.filter(
                    venta=venta,
                    zona=zona_locked
                ).count()
                
                tickets_needed = item.cantidad - existing_tickets
                
                for _ in range(tickets_needed):
                    ticket = Ticket.objects.create(
                        venta=venta,
                        presentacion=zona_locked.presentacion,
                        zona=zona_locked,
                    )
                    
                    # Generar QR
                    qr_file, token = QRCodeService.generar_qr(
                        codigo_uuid=str(ticket.codigo_uuid),
                        ticket_id=ticket.id,
                        usar_encriptacion=True
                    )
                    
                    if token:
                        ticket.token_encriptado = token
                    
                    ticket.qr_image.save(
                        f'ticket_{ticket.codigo_uuid}.png',
                        qr_file,
                        save=True
                    )
        
        logger.info(f"Tickets creados/verificados para orden {order.id}")
    
    def _should_create_order_from_cart(
        self,
        external_reference: Optional[str],
        mp_status: str
    ) -> bool:
        """Determinar si se debe crear orden desde carrito"""
        return (
            external_reference
            and external_reference.startswith('cart_')
            and mp_status in ['approved', 'pending', 'in_process']
        )
    
    def _is_rejected_payment(self, mp_status: str) -> bool:
        """Verificar si es un pago rechazado"""
        return mp_status in ['rejected', 'cancelled', 'expired']
    
    def _create_order_from_cart(
        self,
        external_reference: str,
        payment: Dict
    ) -> Optional[Orden]:
        """
        Crear orden desde carrito cuando MP notifica pago
        
        Args:
            external_reference: Referencia del carrito (cart_123)
            payment: Datos del pago
            
        Returns:
            Orden creada o None
        """
        try:
            cart_id = external_reference.replace('cart_', '')
            carrito = Carrito.objects.get(id=cart_id, activo=True)
            
            # Preparar datos del carrito
            items = CarritoItem.objects.filter(carrito=carrito).select_related('zona')
            
            if not items.exists():
                logger.warning(f"Carrito {cart_id} vacío o no encontrado")
                return None
            
            carrito_data = {
                'cliente': carrito.cliente,
                'carrito_id': carrito.id,
                'items': list(items),
            }
            
            mp_status = payment.get('status')
            order_status = PaymentStatusMapper.map_to_order_status(
                mp_status,
                payment.get('status_detail')
            )
            
            order = self.order_creator.create_from_cart(
                carrito_data=carrito_data,
                payment_info={
                    'transaction_amount': payment.get('transaction_amount'),
                    'payment_method_id': payment.get('payment_method_id'),
                    'payment_type_id': payment.get('payment_type_id'),
                    'status_detail': payment.get('status_detail'),
                },
                payment_id=payment.get('id'),
                order_status=order_status,
                external_reference=external_reference,
                mp_status=mp_status
            )
            
            logger.info(
                f"Orden creada desde webhook para carrito {cart_id}, "
                f"paymentId {payment.get('id')}, status {mp_status}"
            )
            return order
            
        except Carrito.DoesNotExist:
            logger.warning(f"Carrito no encontrado: {cart_id}")
            return None
        except Exception as e:
            logger.error(f"Error creando orden desde webhook: {str(e)}")
            return None
    
    def _handle_rejected_payment_without_order(
        self,
        external_reference: Optional[str],
        payment: Dict
    ) -> None:
        """
        Manejar pago rechazado sin orden existente
        
        Args:
            external_reference: Referencia externa
            payment: Datos del pago
        """
        if not external_reference or not external_reference.startswith('cart_'):
            return
        
        cart_id = external_reference.replace('cart_', '')
        
        try:
            carrito = Carrito.objects.get(id=cart_id)
            # El carrito permanece activo para que el usuario pueda reintentar
            logger.info(
                f"Rechazo guardado para carrito {cart_id}, "
                f"paymentId {payment.get('id')}"
            )
        except Carrito.DoesNotExist:
            logger.warning(f"Carrito no encontrado: {cart_id}")
