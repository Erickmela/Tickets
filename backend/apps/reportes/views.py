"""
Views para Reportes - Aplicando Single Responsibility
Responsabilidad: Coordinar endpoints de reportes
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from datetime import datetime

from .services import ReportesService
from .serializers import (
    DashboardSerializer,
    ReporteVentasSerializer,
    ReporteValidacionesSerializer,
    ReporteEventosSerializer,
    ReportePersonalSerializer,
    FiltrosReporteSerializer
)
from .utils import ExportadorPDF, ExportadorExcel


class ReportesViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Reportes y Estadísticas
    Responsabilidad: Endpoints de reportes
    """
    permission_classes = [IsAuthenticated]
    
    def _validar_filtros(self, request):
        """Validar y parsear filtros de la petición"""
        filtros = {
            'fecha_inicio': request.query_params.get('fecha_inicio'),
            'fecha_fin': request.query_params.get('fecha_fin'),
            'evento_id': request.query_params.get('evento_id'),
            'usuario_id': request.query_params.get('usuario_id'),
        }
        
        # Parsear fechas
        if filtros['fecha_inicio']:
            try:
                filtros['fecha_inicio'] = datetime.strptime(
                    filtros['fecha_inicio'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return None, "Formato de fecha_inicio inválido. Use YYYY-MM-DD"
        
        if filtros['fecha_fin']:
            try:
                filtros['fecha_fin'] = datetime.strptime(
                    filtros['fecha_fin'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return None, "Formato de fecha_fin inválido. Use YYYY-MM-DD"
        
        # Parsear IDs
        if filtros['evento_id']:
            try:
                filtros['evento_id'] = int(filtros['evento_id'])
            except ValueError:
                return None, "evento_id debe ser un número entero"
        
        if filtros['usuario_id']:
            try:
                filtros['usuario_id'] = int(filtros['usuario_id'])
            except ValueError:
                return None, "usuario_id debe ser un número entero"
        
        # Validar con serializer
        serializer = FiltrosReporteSerializer(data=filtros)
        if not serializer.is_valid():
            return None, serializer.errors
        
        return serializer.validated_data, None
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """
        Endpoint: GET /api/reportes/dashboard/
        Función: Obtener métricas generales del dashboard
        """
        # Validar filtros
        filtros, error = self._validar_filtros(request)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Solo admin puede ver reportes
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para ver reportes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Obtener métricas
            metricas = ReportesService.get_dashboard_metricas(
                fecha_inicio=filtros.get('fecha_inicio'),
                fecha_fin=filtros.get('fecha_fin')
            )
            
            serializer = DashboardSerializer(metricas)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al generar dashboard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='ventas')
    def reporte_ventas(self, request):
        """
        Endpoint: GET /api/reportes/ventas/
        Función: Generar reporte completo de ventas
        """
        # Validar filtros
        filtros, error = self._validar_filtros(request)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Solo admin puede ver reportes
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para ver reportes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Generar reporte
            reporte = ReportesService.get_reporte_ventas(
                fecha_inicio=filtros.get('fecha_inicio'),
                fecha_fin=filtros.get('fecha_fin'),
                evento_id=filtros.get('evento_id')
            )
            
            serializer = ReporteVentasSerializer(reporte)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte de ventas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='validaciones')
    def reporte_validaciones(self, request):
        """
        Endpoint: GET /api/reportes/validaciones/
        Función: Generar reporte de validaciones
        """
        # Validar filtros
        filtros, error = self._validar_filtros(request)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Solo admin puede ver reportes
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para ver reportes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Generar reporte
            reporte = ReportesService.get_reporte_validaciones(
                fecha_inicio=filtros.get('fecha_inicio'),
                fecha_fin=filtros.get('fecha_fin'),
                evento_id=filtros.get('evento_id')
            )
            
            serializer = ReporteValidacionesSerializer(reporte)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte de validaciones: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='eventos')
    def reporte_eventos(self, request):
        """
        Endpoint: GET /api/reportes/eventos/
        Función: Generar reporte de eventos
        """
        # Validar filtros
        filtros, error = self._validar_filtros(request)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Solo admin puede ver reportes
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para ver reportes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Generar reporte
            reporte = ReportesService.get_reporte_eventos(
                fecha_inicio=filtros.get('fecha_inicio'),
                fecha_fin=filtros.get('fecha_fin')
            )
            
            serializer = ReporteEventosSerializer(reporte)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte de eventos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='personal')
    def reporte_personal(self, request):
        """
        Endpoint: GET /api/reportes/personal/
        Función: Generar reporte de rendimiento del personal
        """
        # Validar filtros
        filtros, error = self._validar_filtros(request)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Solo admin puede ver reportes
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para ver reportes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Generar reporte
            reporte = ReportesService.get_reporte_personal(
                fecha_inicio=filtros.get('fecha_inicio'),
                fecha_fin=filtros.get('fecha_fin'),
                usuario_id=filtros.get('usuario_id')
            )
            
            serializer = ReportePersonalSerializer(reporte)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte de personal: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='exportar-pdf/(?P<tipo_reporte>[^/.]+)')
    def exportar_pdf(self, request, tipo_reporte=None):
        """
        Endpoint: POST /api/reportes/exportar-pdf/{tipo}/
        Función: Exportar reporte a PDF
        """
        # Solo admin puede exportar
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para exportar reportes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Validar filtros desde el body
            filtros_data = request.data
            serializer = FiltrosReporteSerializer(data=filtros_data)
            
            if not serializer.is_valid():
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            filtros = serializer.validated_data
            
            # Generar reporte según tipo
            if tipo_reporte == 'ventas':
                datos = ReportesService.get_reporte_ventas(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin'),
                    evento_id=filtros.get('evento_id')
                )
            elif tipo_reporte == 'validaciones':
                datos = ReportesService.get_reporte_validaciones(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin'),
                    evento_id=filtros.get('evento_id')
                )
            elif tipo_reporte == 'eventos':
                datos = ReportesService.get_reporte_eventos(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin')
                )
            elif tipo_reporte == 'personal':
                datos = ReportesService.get_reporte_personal(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin'),
                    usuario_id=filtros.get('usuario_id')
                )
            else:
                return Response(
                    {'error': 'Tipo de reporte no válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generar PDF
            pdf_content = ExportadorPDF.generar_pdf(tipo_reporte, datos, filtros)
            
            # Retornar PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}.pdf"'
            return response
        
        except Exception as e:
            return Response(
                {'error': f'Error al exportar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='exportar-excel/(?P<tipo_reporte>[^/.]+)')
    def exportar_excel(self, request, tipo_reporte=None):
        """
        Endpoint: POST /api/reportes/exportar-excel/{tipo}/
        Función: Exportar reporte a Excel
        """
        # Solo admin puede exportar
        if request.user.rol != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para exportar reportes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Validar filtros desde el body
            filtros_data = request.data
            serializer = FiltrosReporteSerializer(data=filtros_data)
            
            if not serializer.is_valid():
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            filtros = serializer.validated_data
            
            # Generar reporte según tipo
            if tipo_reporte == 'ventas':
                datos = ReportesService.get_reporte_ventas(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin'),
                    evento_id=filtros.get('evento_id')
                )
            elif tipo_reporte == 'validaciones':
                datos = ReportesService.get_reporte_validaciones(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin'),
                    evento_id=filtros.get('evento_id')
                )
            elif tipo_reporte == 'eventos':
                datos = ReportesService.get_reporte_eventos(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin')
                )
            elif tipo_reporte == 'personal':
                datos = ReportesService.get_reporte_personal(
                    fecha_inicio=filtros.get('fecha_inicio'),
                    fecha_fin=filtros.get('fecha_fin'),
                    usuario_id=filtros.get('usuario_id')
                )
            else:
                return Response(
                    {'error': 'Tipo de reporte no válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generar Excel
            excel_content = ExportadorExcel.generar_excel(tipo_reporte, datos, filtros)
            
            # Retornar Excel
            response = HttpResponse(
                excel_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}.xlsx"'
            return response
        
        except Exception as e:
            return Response(
                {'error': f'Error al exportar Excel: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
