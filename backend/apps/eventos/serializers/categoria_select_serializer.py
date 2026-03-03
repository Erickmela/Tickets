"""
Serializers simples para Categoria (uso en selects)
Responsabilidad: Serialización mínima para dropdowns
"""
from rest_framework import serializers
from apps.eventos.models import Categoria


class CategoriaSelectSerializer(serializers.ModelSerializer):
    """
    Serializer minimalista para Categoria
    Responsabilidad: Solo datos esenciales para selects/dropdowns
    """
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']
        read_only_fields = fields
