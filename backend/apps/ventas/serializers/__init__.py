"""
Serializers para Ventas y Tickets
Módulo refactorizado aplicando Single Responsibility Principle
Organizado según principios SOLID
"""

# Serializers de Ticket
from .ticket_serializers import (
    TicketSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
    TicketValidacionSerializer,
    MarcarTicketUsadoSerializer,
    AnularTicketSerializer
)

# Serializers de Venta
from .venta_serializers import (
    VentaSerializer,
    VentaListSerializer,
    VentaDetailSerializer,
    VentaCreateSerializer,
    AnularVentaSerializer,
    VentaEstadisticasSerializer
)

# Serializers de Orden (MercadoPago futuro)
from .orden_serializers import (
    OrdenSerializer,
    OrdenListSerializer,
    OrdenCreateSerializer,
    OrdenDetailSerializer,
    OrdenItemSerializer,
    OrdenItemSimpleSerializer
)

# Serializers de Carrito
from .carrito_serializers import (
    CarritoSerializer,
    CarritoListSerializer,
    CarritoItemSerializer,
    CarritoItemSimpleSerializer,
    AgregarItemCarritoSerializer,
    ActualizarItemCarritoSerializer,
    LimpiarCarritoSerializer
)

__all__ = [
    # Ticket serializers
    'TicketSerializer',
    'TicketListSerializer',
    'TicketDetailSerializer',
    'TicketValidacionSerializer',
    'MarcarTicketUsadoSerializer',
    'AnularTicketSerializer',
    
    # Venta serializers
    'VentaSerializer',
    'VentaListSerializer',
    'VentaDetailSerializer',
    'VentaCreateSerializer',
    'AnularVentaSerializer',
    'VentaEstadisticasSerializer',
    
    # Orden serializers
    'OrdenSerializer',
    'OrdenListSerializer',
    'OrdenCreateSerializer',
    'OrdenDetailSerializer',
    'OrdenItemSerializer',
    'OrdenItemSimpleSerializer',
    
    # Carrito serializers
    'CarritoSerializer',
    'CarritoListSerializer',
    'CarritoItemSerializer',
    'CarritoItemSimpleSerializer',
    'AgregarItemCarritoSerializer',
    'ActualizarItemCarritoSerializer',
    'LimpiarCarritoSerializer',
]

