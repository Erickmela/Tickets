"""
Views para Validaciones - Control de Acceso
Responsabilidad crítica: Validar tickets en tiempo real en la puerta del evento
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from .models import Validacion
from .serializers import (
    ValidacionSerializer, ValidacionListSerializer, ValidarTicketSerializer
)
from apps.ventas.models import Ticket
from config.encryption import ticket_encryption


class ValidacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de Validaciones
    Responsabilidad: Solo lectura del historial de validaciones
    """
    queryset = Validacion.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ValidacionListSerializer
        return ValidacionSerializer
    
    def get_queryset(self):
        """Filtrar validaciones según rol"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.rol == 'VALIDADOR':
            # Los validadores solo ven sus propias validaciones
            queryset = queryset.filter(validador=user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def mis_validaciones(self, request):
        """Obtener validaciones del validador actual"""
        validaciones = Validacion.objects.filter(validador=request.user)
        serializer = ValidacionListSerializer(validaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_evento(self, request):
        """Obtener validaciones de un evento específico"""
        evento_id = request.query_params.get('evento_id')
        if not evento_id:
            return Response(
                {'error': 'evento_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validaciones = Validacion.objects.filter(ticket__zona__evento_id=evento_id)
        serializer = self.get_serializer(validaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de validaciones"""
        from django.db.models import Count
        from apps.eventos.models import Evento
        
        try:
            evento = Evento.objects.get(activo=True)
            total_validaciones = Validacion.objects.filter(
                ticket__zona__evento=evento
            ).count()
            
            validaciones_por_zona = Validacion.objects.filter(
                ticket__zona__evento=evento
            ).values('ticket__zona__nombre').annotate(
                total=Count('id')
            )
            
            return Response({
                'evento': evento.nombre,
                'total_ingresos': total_validaciones,
                'por_zona': list(validaciones_por_zona)
            })
        except Evento.DoesNotExist:
            return Response(
                {'error': 'No hay eventos activos'},
                status=status.HTTP_404_NOT_FOUND
            )


class ValidarTicketView(APIView):
    """
    Vista para validar un ticket escaneado
    Responsabilidad crítica: ÚNICO PUNTO DE ENTRADA para validar tickets en puerta
    
    FLUJO:
    1. Recibe el UUID del QR escaneado
    2. Busca el ticket en la base de datos
    3. Valida que esté ACTIVO
    4. Crea el registro de validación
    5. Marca el ticket como USADO
    6. Retorna información del titular para verificación física
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Validar un ticket por su código (UUID o Token Encriptado)
        
        SEGURIDAD MEJORADA v2.0:
        - Acepta tokens encriptados AES-256 + HMAC (MÁS SEGURO)
        - Mantiene compatibilidad con UUID para tickets antiguos
        - Detecta manipulación mediante HMAC
        - Solo usuarios con rol VALIDADOR o ADMIN pueden validar
        - Se registra el validador que procesó la entrada
        """
        # Verificar permisos
        if request.user.rol not in ['VALIDADOR', 'ADMIN']:
            return Response(
                {
                    'success': False,
                    'error': 'No tienes permisos para validar tickets'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ValidarTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        codigo_qr = serializer.validated_data['codigo_uuid']  # Puede ser UUID o token encriptado
        ticket = None
        metodo_usado = None
        
        try:
            # MÉTODO 1: Intentar desencriptar como token AES-256 + HMAC (más seguro)
            try:
                payload = ticket_encryption.decrypt_ticket_data(codigo_qr)
                ticket_uuid = payload['uuid']
                metodo_usado = 'ENCRIPTADO_AES256'
                
                # Buscar ticket por UUID desencriptado
                ticket = Ticket.objects.select_related(
                    'zona', 'zona__evento', 'venta'
                ).get(codigo_uuid=ticket_uuid)
                
                # Validación extra: Verificar que el token almacenado coincida (anti-replay)
                if ticket.token_encriptado and ticket.token_encriptado != codigo_qr:
                    return Response({
                        'success': False,
                        'error': 'TOKEN CLONADO',
                        'message': 'Este QR no corresponde al token original del ticket. Posible clonación.',
                        'alerta': 'DENEGAR ACCESO - REPORTAR A SEGURIDAD'
                    }, status=status.HTTP_403_FORBIDDEN)
                
            except (ValueError, KeyError):
                # MÉTODO 2: Fallback a UUID directo (compatibilidad con tickets antiguos)
                metodo_usado = 'UUID_PLANO'
                ticket = Ticket.objects.select_related(
                    'zona', 'zona__evento', 'venta'
                ).get(codigo_uuid=codigo_qr)
            
            # Verificar que el ticket sea del evento activo
            if not ticket.zona.evento.activo:
                return Response({
                    'success': False,
                    'error': 'Ticket no válido',
                    'message': 'Este ticket no pertenece al evento activo'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el ticket ya fue usado
            validacion_previa = Validacion.objects.filter(ticket=ticket).first()
            if validacion_previa:
                return Response({
                    'success': False,
                    'error': 'TICKET YA USADO',
                    'message': f'Este ticket ya fue usado el {validacion_previa.fecha_hora_ingreso.strftime("%d/%m/%Y a las %H:%M:%S")}',
                    'fecha_uso': validacion_previa.fecha_hora_ingreso,
                    'validador': validacion_previa.validador.nombre_completo,
                    'ticket': {
                        'dni_titular': ticket.dni_titular,
                        'nombre_titular': ticket.nombre_titular,
                        'zona': ticket.zona.nombre
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar estado del ticket
            if not ticket.puede_usarse():
                return Response({
                    'success': False,
                    'error': 'TICKET INVÁLIDO',
                    'message': f'Este ticket no puede ser usado. Estado: {ticket.get_estado_display()}',
                    'estado': ticket.estado
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # 1. Crear el registro de validación
                validacion = Validacion.objects.create(
                    ticket=ticket,
                    validador=request.user,
                    observaciones=serializer.validated_data.get('observaciones', ''),
                    ip_address=serializer.validated_data.get('ip_address'),
                    dispositivo=serializer.validated_data.get('dispositivo', '')
                )
                # 2. El ticket se marca como USADO automáticamente por el signal en models.py
                # Si algo falla aquí, se deshace TODO (rollback)
            
            # Respuesta exitosa con datos para verificación física
            return Response({
                'success': True,
                'message': '✓ ACCESO PERMITIDO',
                'metodo_seguridad': metodo_usado,  # Indica qué método de seguridad se usó
                'validacion_id': validacion.id,
                'fecha_hora_ingreso': validacion.fecha_hora_ingreso,
                'ticket': {
                    'dni_titular': ticket.dni_titular,
                    'nombre_titular': ticket.nombre_titular,
                    'zona': ticket.zona.nombre,
                    'precio': float(ticket.zona.precio)
                },
                'instrucciones': [
                    f'1. Verificar DNI físico: {ticket.dni_titular}',
                    f'2. Verificar que el nombre coincida: {ticket.nombre_titular}',
                    '3. Una vez verificado, permitir el ingreso'
                ]
            }, status=status.HTTP_200_OK)
        
        except Ticket.DoesNotExist:
            # Código UUID no existe = Ticket falso/clonado
            return Response({
                'success': False,
                'error': 'TICKET FALSO',
                'message': 'Este código QR no corresponde a ningún ticket válido. Posible clonación.',
                'alerta': 'DENEGAR ACCESO INMEDIATAMENTE'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except DjangoValidationError as e:
            return Response({
                'success': False,
                'error': 'Error de validación',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Error del sistema',
                'message': f'Error inesperado: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
