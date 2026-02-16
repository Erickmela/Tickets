from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, TicketViewSet, CrearVentaView

router = DefaultRouter()
router.register('ventas', VentaViewSet, basename='venta')
router.register('tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    path('crear-venta/', CrearVentaView.as_view(), name='crear-venta'),
]
