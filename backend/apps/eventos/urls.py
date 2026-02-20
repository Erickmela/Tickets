from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet, ZonaViewSet, CategoriaViewSet


router = DefaultRouter()
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('eventos', EventoViewSet, basename='evento')
router.register('zonas', ZonaViewSet, basename='zona')

urlpatterns = [
    path('', include(router.urls)),
]
