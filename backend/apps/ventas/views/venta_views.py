"""
Views para Venta
Responsabilidad: CRUD y acciones sobre ventas
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.ventas.models import Venta
from apps.ventas.serializers import (
    VentaSerializer, 
    VentaListSerializer, 
    VentaCreateSerializer
)
from apps.ventas.services import VentaService
from apps.ventas.services.queue_service import VirtualQueueService
from config.throttling import CompraRateThrottle

class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Ventas
    Responsabilidad: CRUD y consultas de ventas
    Con throttling específico para limitar compras masivas
    """
    queryset = Venta.objects.select_related(
        'vendedor', 
        'cliente_pagador',
        'orden'
    ).prefetch_related(
        'tickets',
        'tickets__zona'
    ).all()
    permission_classes = [IsAuthenticated]
    throttle_classes = [CompraRateThrottle]  # Limitar compras por cliente
    filter_backends = [filters.SearchFilter]
    search_fields = ['cliente_pagador__dni', 'cliente_pagador__nombre_completo', 'vendedor__username']
    lookup_field = 'codigo_venta'  # Usar código UUID en lugar de ID numérico
    
    def get_serializer_class(self):
        """Seleccionar serializer según acción"""
        if self.action == 'list':
            return VentaListSerializer
        return VentaSerializer
    
    def get_queryset(self):
        """Filtrar ventas según rol del usuario"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.rol == 'VENDEDOR':
            # Los vendedores solo ven sus propias ventas
            queryset = queryset.filter(vendedor=user)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='check-queue')
    def check_queue(self, request):
        """
        Verificar estado en la cola virtual antes de comprar
        Endpoint: POST /api/ventas/ventas/check-queue/
        Body: { "evento_slug": "gran-concierto-2026" }
        """
        evento_slug = request.data.get('evento_slug')
        
        if not evento_slug:
            return Response(
                {'error': 'evento_slug es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Staff (ADMIN, VALIDADOR, VENDEDOR) saltea la cola
        if VirtualQueueService.bypass_queue_for_staff(request.user):
            return Response({
                'status': 'active',
                'bypass': True,
                'message': 'Usuario staff - Sin cola'
            })
        
        # Verificar si hay alta demanda
        if VirtualQueueService.is_high_demand_event(evento_slug):
            # Unirse a la cola
            queue_status = VirtualQueueService.join_queue(
                request.user.id,
                evento_slug
            )
            return Response(queue_status)
        
        # No hay cola, puede comprar directamente
        # Activar al usuario para que pueda proceder
        VirtualQueueService.activate_user(request.user.id, evento_slug)
        return Response({
            'status': 'active',
            'no_queue': True,
            'message': 'Puedes proceder con la compra'
        })
    
    @action(detail=False, methods=['get'], url_path='queue-position')
    def queue_position(self, request):
        """
        Obtener posición actual en la cola
        Endpoint: GET /api/ventas/ventas/queue-position/?evento_slug=gran-concierto-2026
        """
        evento_slug = request.query_params.get('evento_slug')
        
        if not evento_slug:
            return Response(
                {'error': 'evento_slug es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Staff siempre está activo
        if VirtualQueueService.bypass_queue_for_staff(request.user):
            return Response({'status': 'active', 'bypass': True})
        
        # Obtener posición
        position_data = VirtualQueueService.get_queue_position(
            request.user.id,
            evento_slug
        )
        
        return Response(position_data)
    
    @action(detail=False, methods=['post'], url_path='leave-queue')
    def leave_queue(self, request):
        """
        Salir de la cola (usuario cancela o completa compra)
        Endpoint: POST /api/ventas/ventas/leave-queue/
        Body: { "evento_slug": "gran-concierto-2026" }
        """
        evento_slug = request.data.get('evento_slug')
        
        if not evento_slug:
            return Response(
                {'error': 'evento_slug es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        VirtualQueueService.deactivate_user(request.user.id, evento_slug)
        
        return Response({
            'message': 'Saliste de la cola correctamente',
            'status': 'left_queue'
        })
    
    @action(detail=False, methods=['get'], url_path='queue-stats', permission_classes=[IsAuthenticated])
    def queue_stats(self, request):
        """
        Estadísticas de la cola (solo para ADMIN)
        Endpoint: GET /api/ventas/ventas/queue-stats/?evento_slug=gran-concierto-2026
        """
        # Solo ADMIN puede ver estadísticas
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para ver estadísticas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        evento_slug = request.query_params.get('evento_slug')
        
        if not evento_slug:
            return Response(
                {'error': 'evento_slug es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stats = VirtualQueueService.get_queue_stats(evento_slug)
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """
        Anular una venta completa
        Usa transacción atómica para garantizar consistencia
        """
        venta = self.get_object()
        
        if not venta.puede_anularse():
            return Response(
                {'error': 'No se puede anular una venta con tickets ya usados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Anular todos los tickets - si alguno falla, se hace rollback de TODO
                motivo = request.data.get('motivo', 'Anulación de venta')
                for ticket in venta.tickets.all():
                    ticket.anular(motivo)
                
                # Marcar la venta como inactiva
                venta.activo = False
                venta.save()
            
            return Response({'message': 'Venta anulada correctamente'})
            
        except Exception as e:
            return Response(
                {'error': f'Error al anular la venta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CrearVentaView(APIView):
    """
    Vista para crear una venta completa con múltiples tickets
    Responsabilidad única: Coordinar la creación de ventas
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crear una venta con múltiples tickets
        Aplica validaciones de negocio y transaccionalidad
        """
        serializer = VentaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar que el usuario sea vendedor o admin
        if request.user.rol not in ['VENDEDOR', 'ADMIN']:
            return Response(
                {'error': 'No tienes permisos para crear ventas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Usar el servicio para crear la venta
            venta = VentaService.crear_venta(
                vendedor=request.user,
                datos_venta=serializer.validated_data,
                tickets_data=serializer.validated_data['tickets']
            )
            
            # Serializar la respuesta
            response_serializer = VentaSerializer(venta, context={'request': request})
            return Response(
                {
                    'message': 'Venta creada exitosamente',
                    'venta': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al crear la venta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
