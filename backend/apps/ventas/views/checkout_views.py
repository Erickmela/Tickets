"""
Views para Checkout
Responsabilidad: Procesar compras desde el carrito
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.ventas.serializers import CheckoutSerializer
from apps.ventas.services import CheckoutService


class CheckoutViewSet(viewsets.ViewSet):
    """
    ViewSet para procesar checkout
    Solo permite POST para crear órdenes desde carrito
    """
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """
        Procesar checkout desde carrito
        
        Recibe:
        - metodo_pago: str (tarjeta, efectivo, transferencia)
        - nro_operacion: str (opcional)
        - items: list[{presentacion_id, zona_id, cantidad}]
        
        Retorna:
        - orden_id: UUID de la orden creada
        - venta_id: UUID de la venta creada
        - tickets: list[{uuid, codigo_qr_url}]
        - total: Decimal
        """
        serializer = CheckoutSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Datos de checkout inválidos',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validar disponibilidad antes de procesar
            validacion = CheckoutService.validar_disponibilidad(
                serializer.validated_data['items']
            )
            
            if not validacion['valido']:
                return Response(
                    {
                        'error': 'Disponibilidad insuficiente',
                        'details': validacion['errores']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Procesar checkout
            resultado = CheckoutService.procesar_checkout(
                cliente=request.user.perfil_cliente,
                metodo_pago=serializer.validated_data['metodo_pago'],
                items_data=serializer.validated_data['items'],
                nro_operacion=serializer.validated_data.get('nro_operacion')
            )
            
            return Response(
                {
                    'success': True,
                    'message': 'Compra procesada exitosamente',
                    'data': resultado
                },
                status=status.HTTP_201_CREATED
            )
            
        except DjangoValidationError as e:
            return Response(
                {
                    'error': 'Error de validación',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {
                    'error': 'Datos inválidos',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Error al procesar la compra',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
