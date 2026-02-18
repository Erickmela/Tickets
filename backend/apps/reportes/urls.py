"""
URLs para Reportes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportesViewSet

router = DefaultRouter()
router.register(r'reportes', ReportesViewSet, basename='reportes')

urlpatterns = [
    path('', include(router.urls)),
]
