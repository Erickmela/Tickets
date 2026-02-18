"""
Views para Ventas y Tickets
Módulo refactorizado aplicando Single Responsibility Principle
"""
from .venta_views import VentaViewSet, CrearVentaView
from .ticket_views import TicketViewSet

__all__ = [
    'VentaViewSet',
    'CrearVentaView',
    'TicketViewSet',
]
