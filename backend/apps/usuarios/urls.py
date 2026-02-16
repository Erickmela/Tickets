from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrabajadorViewSet, ClienteViewSet, LoginView, LogoutView

router = DefaultRouter()
router.register('usuarios', TrabajadorViewSet, basename='trabajador')
router.register('clientes', ClienteViewSet, basename='cliente')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
