"""
Clases de paginación personalizadas para el sistema
"""
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Paginación personalizada que permite al cliente especificar el tamaño de página
    """
    page_size = 10  # Tamaño por defecto
    page_size_query_param = 'page_size'  # Parámetro para cambiar el tamaño
    max_page_size = 100  # Tamaño máximo permitido
    page_query_param = 'page'  # Parámetro para el número de página
