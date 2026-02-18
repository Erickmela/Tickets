"""
Serializers para Reportes - Aplicando Single Responsibility
Responsabilidad: Serializar datos de reportes
"""
from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    """Serializer para métricas del dashboard"""
    total_ventas = serializers.IntegerField()
    total_tickets = serializers.IntegerField()
    total_validados = serializers.IntegerField()
    ingresos_totales = serializers.DecimalField(max_digits=10, decimal_places=2)
    tasa_validacion = serializers.FloatField()


class ReporteVentasSerializer(serializers.Serializer):
    """Serializer para reporte de ventas"""
    resumen = DashboardSerializer()
    grafico = serializers.ListField(
        child=serializers.DictField()
    )
    detalles = serializers.ListField(
        child=serializers.DictField()
    )


class ReporteValidacionesSerializer(serializers.Serializer):
    """Serializer para reporte de validaciones"""
    total_validaciones = serializers.IntegerField()
    validaciones_exitosas = serializers.IntegerField()
    validaciones_fallidas = serializers.IntegerField()
    grafico = serializers.ListField(
        child=serializers.DictField()
    )
    detalles = serializers.ListField(
        child=serializers.DictField()
    )


class ReporteEventosSerializer(serializers.Serializer):
    """Serializer para reporte de eventos"""
    total_eventos = serializers.IntegerField()
    eventos_activos = serializers.IntegerField()
    eventos_finalizados = serializers.IntegerField()
    ocupacion_promedio = serializers.FloatField()
    detalles = serializers.ListField(
        child=serializers.DictField()
    )


class ReportePersonalSerializer(serializers.Serializer):
    """Serializer para reporte de personal"""
    total_vendedores = serializers.IntegerField()
    total_validadores = serializers.IntegerField()
    detalles = serializers.ListField(
        child=serializers.DictField()
    )


class FiltrosReporteSerializer(serializers.Serializer):
    """Serializer para validar filtros de reportes"""
    fecha_inicio = serializers.DateField(required=False, allow_null=True)
    fecha_fin = serializers.DateField(required=False, allow_null=True)
    evento_id = serializers.IntegerField(required=False, allow_null=True)
    usuario_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, data):
        """Validar que fecha_fin sea mayor que fecha_inicio"""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                "La fecha fin debe ser mayor o igual a la fecha inicio"
            )
        
        return data
