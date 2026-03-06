"""
Throttling personalizado por roles
Responsabilidad: Limitar peticiones por tipo de usuario para proteger el servidor
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class ClienteRateThrottle(UserRateThrottle):
    """
    Límite para usuarios CLIENTE
    Protege el servidor de uso excesivo pero permite navegación normal
    """
    scope = 'cliente'
    
    def allow_request(self, request, view):
        # Staff (ADMIN, VALIDADOR, VENDEDOR) no tiene límites
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'rol'):
                if request.user.rol in ['ADMIN', 'VALIDADOR', 'VENDEDOR']:
                    return True  # Sin límites para staff
        
        # Aplicar límite solo a CLIENTE
        return super().allow_request(request, view)


class CompraRateThrottle(UserRateThrottle):
    """
    Límite específico para operaciones de compra/venta
    Evita compras masivas accidentales o bots
    """
    scope = 'compra'
    
    def allow_request(self, request, view):
        # Staff siempre puede crear ventas sin límites
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'rol'):
                if request.user.rol in ['ADMIN', 'VALIDADOR', 'VENDEDOR']:
                    return True
        
        # Aplicar límite solo a CLIENTE
        return super().allow_request(request, view)


class AnonimoRateThrottle(AnonRateThrottle):
    """
    Límite para usuarios no autenticados (visitantes)
    Más restrictivo para proteger endpoints públicos
    """
    scope = 'anon'
