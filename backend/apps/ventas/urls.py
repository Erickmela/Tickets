from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, TicketViewSet, CrearVentaView, CheckoutViewSet, CarritoViewSet
from .views.mercadopago_views import MercadoPagoViewSet

router = DefaultRouter()
router.register('ventas', VentaViewSet, basename='venta')
router.register('tickets', TicketViewSet, basename='ticket')
router.register('checkout', CheckoutViewSet, basename='checkout')
router.register('carritos', CarritoViewSet, basename='carrito')
router.register('mercadopago', MercadoPagoViewSet, basename='mercadopago')

urlpatterns = [
    path('', include(router.urls)),
    path('crear-venta/', CrearVentaView.as_view(), name='crear-venta'),
]
