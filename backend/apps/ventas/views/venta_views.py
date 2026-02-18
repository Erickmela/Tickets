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
    CrearVentaSerializer
)
from apps.ventas.services import VentaService


class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Ventas
    Responsabilidad: CRUD y consultas de ventas
    """
    queryset = Venta.objects.select_related('vendedor', 'cliente_pagador').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['cliente_pagador__dni', 'cliente_pagador__nombre_completo', 'vendedor__username']
    
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
    
    @action(detail=False, methods=['get'])
    def mis_ventas(self, request):
        """Obtener ventas del vendedor actual"""
        ventas = Venta.objects.filter(vendedor=request.user)
        serializer = VentaListSerializer(ventas, many=True)
        return Response(serializer.data)
    
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
        serializer = CrearVentaSerializer(data=request.data)
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
