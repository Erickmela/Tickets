from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.eventos.models import Categoria
from apps.eventos.serializers.categoria_serializers import CategoriaSerializer
from apps.eventos.serializers.categoria_select_serializer import CategoriaSelectSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'], url_path='select')
    def select_options(self, request):
        """
        Retorna solo ID y nombre de categorías activas
        """
        categorias = Categoria.objects.filter(
            estado='1',  # Solo activas por estado
            activo=True   # Solo activas por campo activo
        ).order_by('nombre')
        
        serializer = CategoriaSelectSerializer(categorias, many=True)
        return Response(serializer.data)
