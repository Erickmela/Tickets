from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ValidacionViewSet, ValidarTicketView

router = DefaultRouter()
router.register('validaciones', ValidacionViewSet, basename='validacion')

urlpatterns = [
    path('', include(router.urls)),
    path('validar-ticket/', ValidarTicketView.as_view(), name='validar-ticket'),
]
