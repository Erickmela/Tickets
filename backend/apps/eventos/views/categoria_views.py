from rest_framework import viewsets, permissions
from apps.eventos.models import Categoria
from apps.eventos.serializers.categoria_serializers import CategoriaSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
