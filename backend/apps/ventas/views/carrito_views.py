"""
Views para Carrito
Responsabilidad: Gestionar carritos temporales para checkout
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.ventas.models import Carrito, CarritoItem
from apps.ventas.serializers import CarritoSerializer, CarritoItemSerializer


class CarritoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar carritos de compra
    """
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Solo mostrar carritos del usuario actual"""
        return Carrito.objects.filter(
            cliente__usuario=self.request.user
        ).prefetch_related('items', 'items__zona')
    
    @action(detail=False, methods=['get'])
    def activo(self, request):
        """Obtener o crear el carrito activo del usuario"""
        carrito, created = Carrito.objects.get_or_create(
            cliente=request.user.perfil_cliente,
            activo=True,
            defaults={'activo': True}
        )
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def sincronizar(self, request):
        """
        Sincronizar carrito del frontend (localStorage) con el backend
        
        Body:
        {
            "items": [
                {
                    "presentacion_id": 1,
                    "zona_id": 2,
                    "cantidad": 3
                }
            ]
        }
        
        Returns el carrito creado/actualizado
        """
        items_data = request.data.get('items', [])
        
        if not items_data:
            return Response(
                {'error': 'No se proporcionaron items'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Desactivar carritos anteriores
                Carrito.objects.filter(
                    cliente=request.user.perfil_cliente,
                    activo=True
                ).update(activo=False)
                
                # Crear nuevo carrito
                carrito = Carrito.objects.create(
                    cliente=request.user.perfil_cliente,
                    activo=True
                )
                
                # Agregar items
                for item_data in items_data:
                    from apps.eventos.models import Zona
                    
                    zona = Zona.objects.select_related(
                        'presentacion', 
                        'presentacion__evento'
                    ).get(id=item_data['zona_id'])
                    
                    # Validar disponibilidad
                    if not zona.tiene_disponibilidad(item_data['cantidad']):
                        raise ValueError(f'No hay suficientes tickets disponibles en la zona {zona.nombre}')
                    
                    CarritoItem.objects.create(
                        carrito=carrito,
                        zona=zona,
                        cantidad=item_data['cantidad']
                    )
                
                serializer = self.get_serializer(carrito)
                return Response(
                    {
                        'success': True,
                        'carrito': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
                
        except Zona.DoesNotExist:
            return Response(
                {'error': 'Una o más zonas no existen'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al sincronizar carrito: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def agregar_item(self, request, pk=None):
        """Agregar item al carrito"""
        carrito = self.get_object()
        
        zona_id = request.data.get('zona_id')
        cantidad = request.data.get('cantidad', 1)
        
        if not zona_id:
            return Response(
                {'error': 'zona_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.eventos.models import Zona
            zona = Zona.objects.get(id=zona_id)
            
            # Verificar si el item ya existe
            item_existente = CarritoItem.objects.filter(
                carrito=carrito,
                zona=zona
            ).first()
            
            if item_existente:
                item_existente.cantidad += cantidad
                item_existente.save()
                item_serializer = CarritoItemSerializer(item_existente)
            else:
                item = CarritoItem.objects.create(
                    carrito=carrito,
                    zona=zona,
                    cantidad=cantidad
                )
                item_serializer = CarritoItemSerializer(item)
            
            return Response(item_serializer.data)
            
        except Zona.DoesNotExist:
            return Response(
                {'error': 'La zona no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def limpiar(self, request, pk=None):
        """Limpiar todos los items del carrito"""
        carrito = self.get_object()
        carrito.items.all().delete()
        return Response({'message': 'Carrito limpiado'})
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar carrito y sus items"""
        carrito = self.get_object()
        carrito.delete()
        return Response(
            {'message': 'Carrito eliminado'},
            status=status.HTTP_204_NO_CONTENT
        )
