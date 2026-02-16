"""
Custom Authentication Classes
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication sin verificación CSRF para APIs REST.
    CSRF no es necesario cuando se usa CORS correctamente.
    """
    def enforce_csrf(self, request):
        return  # No forzar la verificación CSRF
