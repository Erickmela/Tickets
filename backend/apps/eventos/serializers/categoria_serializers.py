from rest_framework import serializers
from apps.eventos.models import Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = [
            'id',
            'nombre',
            'slug',
            'imagen_path',
            'estado',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'slug', 'fecha_creacion', 'fecha_actualizacion']
