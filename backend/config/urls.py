"""
URL Configuration - Principio de Interface Segregation
Rutas organizadas por módulo de negocio
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Jala Jala Tickets API",
      default_version='v1',
      description="Sistema de gestión de tickets con seguridad anti-clonación",
      contact=openapi.Contact(email="contacto@jalajala.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints - Segregación por dominio
    path('api/usuarios/', include('apps.usuarios.urls')),
    path('api/eventos/', include('apps.eventos.urls')),
    path('api/ventas/', include('apps.ventas.urls')),
    path('api/validaciones/', include('apps.validaciones.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
