"""
Vistas de MercadoPago para Checkout Pro
Responsabilidad: Crear preferencias de pago y procesar webhooks
"""
import logging
import mercadopago
from decimal import Decimal
from typing import Dict, List, Optional

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from apps.ventas.models import Orden, Carrito, CarritoItem
from apps.ventas.services.mercadopago_webhook_service import MercadoPagoWebhookService
from apps.ventas.services.webhook_validation_service import WebhookValidationService
from apps.ventas.services.payment_status_mapper import PaymentStatusMapper

logger = logging.getLogger(__name__)


class MercadoPagoViewSet(viewsets.ViewSet):
    """
    ViewSet para manejo de MercadoPago Checkout Pro
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webhook_service = MercadoPagoWebhookService()
        self.validation_service = WebhookValidationService()
        self._sdk = None
    
    def get_permissions(self):
        """Solo el webhook es público, el resto requiere autenticación"""
        if self.action == 'webhook_notification':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @property
    def sdk(self):
        """Inicializar SDK de MercadoPago (lazy loading)"""
        if self._sdk is None:
            access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
            if not access_token:
                logger.error('MERCADOPAGO_ACCESS_TOKEN no configurado')
                return None
            
            self._sdk = mercadopago.SDK(access_token)
        return self._sdk
    
    @action(detail=False, methods=['post'])
    def create_preference(self, request: Request):
        """
        Crear preferencia de pago desde el carrito del usuario
        
        POST /api/ventas/mercadopago/create_preference/
        
        Body:
        {
            "carrito_id": 123  # Opcional, toma el carrito activo del usuario
        }
        
        Returns:
        {
            "preference_id": "xxx",
            "init_point": "https://...",
            "sandbox_init_point": "https://..."
        }
        """
        try:
            # Obtener carrito
            carrito_id = request.data.get('carrito_id')
            
            if carrito_id:
                carrito = Carrito.objects.get(
                    id=carrito_id,
                    cliente__usuario=request.user,
                    activo=True
                )
            else:
                carrito = Carrito.objects.filter(
                    cliente__usuario=request.user,
                    activo=True
                ).first()
            
            if not carrito:
                return Response(
                    {'error': 'No se encontró un carrito activo'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener items del carrito
            items = CarritoItem.objects.filter(carrito=carrito).select_related(
                'zona',
                'zona__presentacion',
                'zona__presentacion__evento'
            )
            
            if not items.exists():
                return Response(
                    {'error': 'El carrito está vacío'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear preferencia
            preference_data = self._build_preference_request(
                carrito=carrito,
                items=list(items),
                customer=carrito.cliente
            )
            
            if not self.sdk:
                return Response(
                    {'error': 'Error de configuración de MercadoPago'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            preference_response = self.sdk.preference().create(preference_data)
            preference = preference_response.get('response', {})
            
            if preference_response.get('status') != 201:
                logger.error(f'Error creando preferencia: {preference_response}')
                return Response(
                    {'error': 'Error al crear preferencia de pago'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Guardar preference_id en una orden preliminar
            orden = Orden.objects.create(
                cliente=carrito.cliente,
                total=self._calculate_total(items),
                mp_preference_id=preference.get('id'),
                estado='pendiente',
            )
            
            logger.info(f'Preferencia creada: {preference.get("id")} para carrito {carrito.id}')
            
            return Response({
                'preference_id': preference.get('id'),
                'init_point': preference.get('init_point'),
                'sandbox_init_point': preference.get('sandbox_init_point'),
                'orden_id': orden.id,
            })
            
        except Carrito.DoesNotExist:
            return Response(
                {'error': 'Carrito no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error creando preferencia: {str(e)}', exc_info=True)
            return Response(
                {'error': 'Error al procesar la solicitud'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @method_decorator(csrf_exempt)
    def webhook_notification(self, request: Request):
        """
        Endpoint para recibir notificaciones de MercadoPago
        
        POST /api/ventas/mercadopago/webhook_notification/
        
        MercadoPago enviará notificaciones aquí cuando el estado del pago cambie
        """
        logger.info('Notificación MP recibida')
        
        # Extraer datos de la notificación
        notification_type = request.data.get('type') or request.data.get('topic')
        payment_id = request.data.get('data', {}).get('id') or request.data.get('id')
        
        # Validar que sea una notificación de pago
        if not self.validation_service.is_payment_notification(notification_type):
            logger.warning(f'Notificación MP inválida: tipo {notification_type}')
            return Response({'message': 'invalid notification type'}, status=400)
        
        if not payment_id:
            logger.warning('Notificación MP inválida: falta payment_id')
            return Response({'message': 'missing payment id'}, status=400)
        
        # Validar firma si es webhook (y no IPN)
        has_action = 'action' in request.data
        is_production = not settings.DEBUG
        
        if has_action:
            signature = request.META.get('HTTP_X_SIGNATURE')
            data_id = request.GET.get('data_id')
            x_request_id = request.META.get('HTTP_X_REQUEST_ID')
            
            if not self.validation_service.validate_signature(
                signature=signature,
                data_id=data_id,
                x_request_id=x_request_id,
                is_production=is_production
            ):
                logger.warning(f'Firma de webhook inválida para paymentId: {payment_id}')
                return Response({'message': 'invalid signature'}, status=401)
        
        # Obtener información del pago desde MP
        if not self.sdk:
            logger.error('No se puede procesar webhook: SDK no configurado')
            return Response({'message': 'configuration error'}, status=500)
        
        try:
            payment_response = self.sdk.payment().get(payment_id)
            payment = payment_response.get('response', {})
            
            if payment_response.get('status') != 200:
                logger.error(f'Error obteniendo pago {payment_id}: {payment_response}')
                return Response({'message': 'error fetching payment'}, status=500)
            
            logger.info(f'Payment obtenido: {payment.get("status")} - ID: {payment_id}')
            
        except Exception as e:
            logger.error(f'Error obteniendo pago {payment_id}: {str(e)}')
            return Response({'message': 'error fetching payment'}, status=500)
        
        # Procesar el webhook
        try:
            self.webhook_service.process_webhook(
                webhook_data={
                    'payment_id': payment_id,
                    'is_webhook': has_action,
                },
                payment=payment
            )
            
            return Response({'message': 'ok'}, status=200)
            
        except Exception as e:
            logger.error(f'Error procesando webhook: {str(e)}', exc_info=True)
            return Response({'message': 'processing error'}, status=500)
    
    @action(detail=False, methods=['get'])
    def payment_status(self, request: Request):
        """
        Consultar estado de un pago
        
        GET /api/ventas/mercadopago/payment_status/?payment_id=xxx
        """
        payment_id = request.query_params.get('payment_id')
        
        if not payment_id:
            return Response(
                {'error': 'payment_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            orden = Orden.objects.get(mp_payment_id=payment_id, cliente__usuario=request.user)
            
            return Response({
                'orden_id': orden.id,
                'estado': orden.estado,
                'mp_status': orden.mp_status,
                'mp_status_detail': orden.mp_status_detail,
                'total': str(orden.total),
                'mensaje': PaymentStatusMapper.get_user_friendly_message(
                    orden.mp_status,
                    orden.mp_status_detail
                )
            })
            
        except Orden.DoesNotExist:
            return Response(
                {'error': 'Pago no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _build_preference_request(
        self,
        carrito: Carrito,
        items: List[CarritoItem],
        customer
    ) -> Dict:
        """
        Construir el request de preferencia para MercadoPago
        
        Args:
            carrito: Carrito del cliente
            items: Items del carrito
            customer: Cliente (PerfilCliente)
            
        Returns:
            Dict con la estructura de preferencia de MP
        """
        # Construir items
        mp_items = []
        for item in items:
            mp_items.append({
                'id': str(item.zona.id),
                'title': f'{item.zona.presentacion.evento.nombre} - {item.zona.nombre}',
                'description': f'Zona {item.zona.nombre} - {item.zona.presentacion.evento.nombre}',
                'category_id': 'tickets',
                'quantity': item.cantidad,
                'unit_price': float(item.zona.precio),
                'currency_id': 'PEN',
            })
        
        # Información del pagador
        payer = {
            'name': customer.usuario.first_name or '',
            'surname': customer.usuario.last_name or '',
            'email': customer.usuario.email,
        }
        
        if hasattr(customer, 'dni') and customer.dni:
            payer['identification'] = {
                'type': 'DNI',
                'number': str(customer.dni),
            }
        
        # URLs de retorno
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        back_urls = {
            'success': f'{base_url}/pago/success',
            'pending': f'{base_url}/pago/pending',
            'failure': f'{base_url}/pago/failure',
        }
        
        # Construir preferencia
        preference = {
            'items': mp_items,
            'payer': payer,
            'back_urls': back_urls,
            'auto_return': 'approved',
            'external_reference': f'cart_{carrito.id}',
            'statement_descriptor': getattr(settings, 'MERCADOPAGO_STATEMENT_DESCRIPTOR', 'TICKETS'),
            'notification_url': self._get_notification_url(request=None),
            'binary_mode': True,
            'expires': False,
            'payment_methods': {
                'installments': 1,
                'default_installments': 1,
            }
        }
        
        return preference
    
    def _get_notification_url(self, request: Optional[Request] = None) -> str:
        """Obtener URL de notificación para webhooks"""
        base_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
        return f'{base_url}/api/ventas/mercadopago/webhook_notification/?source_news=webhooks'
    
    def _calculate_total(self, items: List[CarritoItem]) -> Decimal:
        """Calcular total del carrito"""
        total = Decimal('0.00')
        for item in items:
            total += item.zona.precio * item.cantidad
        return total
