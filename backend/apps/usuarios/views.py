"""
Views para Usuarios - Arquitectura Unificada
Single Responsibility: Cada view tiene una responsabilidad específica
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Usuario, PerfilCliente, RolUsuario
from .serializers import (
    UsuarioConPerfilSerializer, TrabajadorCreateSerializer, TrabajadorUpdateSerializer,
    ClienteCreateSerializer, ClienteUpdateSerializer,
    UsuarioLoginSerializer, PerfilClienteSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TrabajadorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Trabajadores (Usuarios con rol ADMIN/VENDEDOR/VALIDADOR)
    Responsabilidad: CRUD de trabajadores del sistema
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'perfil_cliente__nombre_completo', 'perfil_cliente__dni']
    
    def get_queryset(self):
        """Obtener solo trabajadores (excluir rol CLIENTE)"""
        queryset = Usuario.objects.exclude(rol=RolUsuario.CLIENTE).select_related('perfil_cliente')
        
        # Filtro por rol
        rol = self.request.query_params.get('rol', '')
        if rol:
            queryset = queryset.filter(rol=rol)
        
        return queryset.order_by('-fecha_creacion')
    
    def get_serializer_class(self):
        """Seleccionar serializer según acción"""
        if self.action == 'create':
            return TrabajadorCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TrabajadorUpdateSerializer
        return UsuarioConPerfilSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear nuevo trabajador"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Retornar con el serializer de lectura
        instance = serializer.instance
        output_serializer = UsuarioConPerfilSerializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """Actualizar trabajador"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Retornar con el serializer de lectura
        output_serializer = UsuarioConPerfilSerializer(instance)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_activo(self, request, pk=None):
        """Activar/Desactivar trabajador"""
        trabajador = self.get_object()
        trabajador.is_active = not trabajador.is_active
        trabajador.save()
        
        serializer = UsuarioConPerfilSerializer(trabajador)
        return Response({
            'message': f'Trabajador {"activado" if trabajador.is_active else "desactivado"} correctamente',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Clientes (Usuarios con rol CLIENTE)
    Responsabilidad: CRUD de clientes/compradores
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['dni', 'nombre_completo', 'usuario__email', 'telefono']
    
    def get_permissions(self):
        """
        Permisos personalizados por acción:
        - create: Público (AllowAny) - Permitir registro sin autenticación
        - Resto: Requiere autenticación
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Obtener solo clientes (rol CLIENTE)"""
        queryset = PerfilCliente.objects.filter(
            usuario__rol=RolUsuario.CLIENTE
        ).select_related('usuario')
        
        return queryset.order_by('-fecha_registro')
    
    def get_serializer_class(self):
        """Seleccionar serializer según acción"""
        if self.action == 'create':
            return ClienteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClienteUpdateSerializer
        return PerfilClienteSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear nuevo cliente"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Retornar con el serializer de lectura
        instance = serializer.instance
        output_serializer = PerfilClienteSerializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """Actualizar cliente"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Retornar con el serializer de lectura
        output_serializer = PerfilClienteSerializer(instance)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'])
    def buscar_por_dni(self, request):
        """Buscar cliente por DNI - Endpoint específico"""
        dni = request.query_params.get('dni')
        if not dni:
            return Response(
                {'error': 'DNI es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cliente = PerfilCliente.objects.get(dni=dni, usuario__rol=RolUsuario.CLIENTE)
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
        except PerfilCliente.DoesNotExist:
            return Response(
                {'message': 'Cliente no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['put', 'patch'])
    def mi_perfil(self, request):
        """Actualizar perfil del cliente autenticado"""
        try:
            perfil = PerfilCliente.objects.get(usuario=request.user)
            serializer = ClienteUpdateSerializer(perfil, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Retornar con el serializer de lectura
            output_serializer = PerfilClienteSerializer(perfil)
            return Response(output_serializer.data)
        except PerfilCliente.DoesNotExist:
            return Response(
                {'error': 'No se encontró el perfil del cliente'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class LoginView(APIView):
    """
    Vista para autenticación de usuarios - Login flexible
    Responsabilidad única: Procesar login con username O DNI
    
    Acepta dos formatos:
    - Trabajadores: username directo (ej: "erickson_admin")
    - Clientes: DNI (ej: "73052183") - se convierte automáticamente a username
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UsuarioLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username_or_dni = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Intentar autenticar directamente con username
        user = authenticate(request, username=username_or_dni, password=password)
        
        # Si falla y parece ser un DNI (8 dígitos), buscar el username del cliente
        if user is None and username_or_dni.isdigit() and len(username_or_dni) == 8:
            try:
                # Buscar el PerfilCliente por DNI
                perfil = PerfilCliente.objects.select_related('usuario').get(dni=username_or_dni)
                
                # Si tiene usuario vinculado, intentar autenticar con su username
                if perfil.usuario:
                    user = authenticate(request, username=perfil.usuario.username, password=password)
            except PerfilCliente.DoesNotExist:
                pass
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Obtener datos del perfil si existe
                perfil_data = {}
                if hasattr(user, 'perfil_cliente'):
                    perfil_data = {
                        'dni': user.perfil_cliente.dni,
                        'telefono': user.perfil_cliente.telefono
                    }
                
                return Response({
                    'message': 'Login exitoso',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'nombre_completo': user.nombre_completo if not hasattr(user, 'perfil_cliente') else user.perfil_cliente.nombre_completo,
                        'email': user.email,
                        'rol': user.rol,
                        **perfil_data
                    }
                })
            else:
                return Response(
                    {'error': 'Usuario inactivo'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    Vista para cerrar sesión
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout exitoso'})
