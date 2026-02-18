"""
Services para Reportes - Aplicando Single Responsibility
Responsabilidad: Lógica de negocio para cálculos y agregaciones
"""
from django.db.models import Count, Sum, Q, F, Avg, DecimalField
from django.db.models.functions import TruncDate, Coalesce
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.ventas.models import Venta, Ticket
from apps.validaciones.models import Validacion
from apps.eventos.models import Evento
from apps.usuarios.models import Usuario


class ReportesService:
    """
    Servicio para generar reportes y estadísticas
    Aplica principio de Responsabilidad Única
    """
    
    @staticmethod
    def get_dashboard_metricas(fecha_inicio=None, fecha_fin=None):
        """
        Obtener métricas generales del dashboard
        """
        # Filtros base
        ventas_filter = Q()
        tickets_filter = Q()
        validaciones_filter = Q()
        
        if fecha_inicio:
            ventas_filter &= Q(fecha_venta__gte=fecha_inicio)
            tickets_filter &= Q(venta__fecha_venta__gte=fecha_inicio)
            validaciones_filter &= Q(fecha_hora_ingreso__gte=fecha_inicio)
        
        if fecha_fin:
            ventas_filter &= Q(fecha_venta__lte=fecha_fin)
            tickets_filter &= Q(venta__fecha_venta__lte=fecha_fin)
            validaciones_filter &= Q(fecha_hora_ingreso__lte=fecha_fin)
        
        # Contar ventas
        total_ventas = Venta.objects.filter(ventas_filter).count()
        
        # Contar tickets (excluyendo anulados)
        total_tickets = Ticket.objects.filter(tickets_filter).exclude(
            estado='ANULADO'
        ).count()
        
        # Contar validaciones (todas son exitosas porque solo se registran si son válidas)
        total_validados = Validacion.objects.filter(validaciones_filter).count()
        
        # Calcular ingresos totales
        ingresos_totales = Venta.objects.filter(ventas_filter).aggregate(
            total=Coalesce(Sum('total_pagado'), Decimal('0.00'))
        )['total']
        
        # Calcular tasa de validación
        tasa_validacion = 0.0
        if total_tickets > 0:
            tasa_validacion = round((total_validados / total_tickets) * 100, 2)
        
        return {
            'total_ventas': total_ventas,
            'total_tickets': total_tickets,
            'total_validados': total_validados,
            'ingresos_totales': float(ingresos_totales),
            'tasa_validacion': tasa_validacion,
        }
    
    @staticmethod
    def get_reporte_ventas(fecha_inicio=None, fecha_fin=None, evento_id=None):
        """
        Generar reporte completo de ventas
        """
        # Filtros
        ventas_filter = Q()
        
        if fecha_inicio:
            ventas_filter &= Q(fecha_venta__gte=fecha_inicio)
        if fecha_fin:
            ventas_filter &= Q(fecha_venta__lte=fecha_fin)
        if evento_id:
            ventas_filter &= Q(tickets__zona__evento_id=evento_id)
        
        # Resumen
        resumen = ReportesService.get_dashboard_metricas(fecha_inicio, fecha_fin)
        
        # Datos para gráfico (agrupados por día)
        grafico = list(
            Venta.objects.filter(ventas_filter)
            .annotate(fecha=TruncDate('fecha_venta'))
            .values('fecha')
            .annotate(
                ventas=Count('id'),
                ingresos=Coalesce(Sum('total_pagado'), Decimal('0.00'))
            )
            .order_by('fecha')[:30]  # Últimos 30 días
        )
        
        # Convertir Decimal a float para JSON
        for item in grafico:
            item['ingresos'] = float(item['ingresos'])
            item['fecha'] = item['fecha'].isoformat()
        
        # Detalles de ventas
        detalles = list(
            Venta.objects.filter(ventas_filter)
            .select_related('vendedor', 'cliente_pagador')
            .values(
                'id',
                'fecha_venta',
                'vendedor__username',
                'cliente_pagador__nombre_completo',
                'total_pagado',
                'metodo_pago'
            )
            .annotate(
                tickets=Count('tickets')
            )
            .order_by('-fecha_venta')[:100]  # Últimas 100 ventas
        )
        
        # Formatear detalles
        for venta in detalles:
            venta['fecha'] = venta.pop('fecha_venta').isoformat()
            venta['vendedor'] = venta.pop('vendedor__username')
            venta['cliente'] = venta.pop('cliente_pagador__nombre_completo') or 'Sin nombre'
            venta['total'] = float(venta.pop('total_pagado'))
        
        return {
            'resumen': resumen,
            'grafico': grafico,
            'detalles': detalles,
        }
    
    @staticmethod
    def get_reporte_validaciones(fecha_inicio=None, fecha_fin=None, evento_id=None):
        """
        Generar reporte de validaciones
        
        NOTA: Solo se registran validaciones exitosas en el sistema
        """
        # Filtros
        validaciones_filter = Q()
        
        if fecha_inicio:
            validaciones_filter &= Q(fecha_hora_ingreso__gte=fecha_inicio)
        if fecha_fin:
            validaciones_filter &= Q(fecha_hora_ingreso__lte=fecha_fin)
        if evento_id:
            validaciones_filter &= Q(ticket__zona__evento_id=evento_id)
        
        # Resumen (todas las validaciones son exitosas)
        validaciones = Validacion.objects.filter(validaciones_filter)
        total_validaciones = validaciones.count()
        validaciones_exitosas = total_validaciones  # Todas son exitosas
        validaciones_fallidas = 0  # No se registran en BD
        
        # Datos para gráfico (agrupados por día)
        grafico = list(
            validaciones
            .annotate(fecha=TruncDate('fecha_hora_ingreso'))
            .values('fecha')
            .annotate(
                validaciones=Count('id')
            )
            .order_by('fecha')[:30]
        )
        
        for item in grafico:
            item['fecha'] = item['fecha'].isoformat()
            item['exitosas'] = item['validaciones']  # Todas son exitosas
            item['fallidas'] = 0  # No se registran
        
        # Detalles
        detalles = list(
            validaciones
            .select_related('ticket__zona__evento', 'validador')
            .values(
                'id',
                'fecha_hora_ingreso',
                'ticket__codigo_uuid',
                'ticket__zona__evento__nombre',
                'validador__username'
            )
            .order_by('-fecha_hora_ingreso')[:100]
        )
        
        for val in detalles:
            val['fecha'] = val.pop('fecha_hora_ingreso').isoformat()
            val['ticket'] = str(val.pop('ticket__codigo_uuid'))
            val['evento'] = val.pop('ticket__zona__evento__nombre')
            val['validador'] = val.pop('validador__username')
            val['estado'] = 'validado'  # Todas son exitosas
        return {
            'total_validaciones': total_validaciones,
            'validaciones_exitosas': validaciones_exitosas,
            'validaciones_fallidas': validaciones_fallidas,
            'grafico': grafico,
            'detalles': detalles,
        }
    
    @staticmethod
    def get_reporte_eventos(fecha_inicio=None, fecha_fin=None):
        """
        Generar reporte de eventos
        """
        # Filtros
        eventos_filter = Q()
        
        if fecha_inicio:
            eventos_filter &= Q(fecha__gte=fecha_inicio)
        if fecha_fin:
            eventos_filter &= Q(fecha__lte=fecha_fin)
        
        eventos = Evento.objects.filter(eventos_filter)
        
        total_eventos = eventos.count()
        eventos_activos = eventos.filter(estado='2').count()  # Activo
        eventos_finalizados = eventos.filter(estado='3').count()  # Finalizado
        
        # Detalles con ocupación
        detalles = []
        for evento in eventos.select_related().prefetch_related('zonas__tickets'):
            # Calcular capacidad total
            capacidad_total = sum(zona.capacidad_maxima for zona in evento.zonas.all())
            
            # Calcular tickets vendidos
            tickets_vendidos = Ticket.objects.filter(
                zona__evento=evento
            ).exclude(estado='ANULADO').count()
            
            # Calcular ocupación
            ocupacion = 0
            if capacidad_total > 0:
                ocupacion = round((tickets_vendidos / capacidad_total) * 100, 1)
            
            detalles.append({
                'id': evento.id,
                'nombre': evento.nombre,
                'fecha': evento.fecha.isoformat(),
                'vendidos': tickets_vendidos,
                'disponibles': capacidad_total - tickets_vendidos,
                'ocupacion': ocupacion,
            })
        
        # Ocupación promedio
        ocupacion_promedio = 0.0
        if detalles:
            ocupacion_promedio = round(
                sum(d['ocupacion'] for d in detalles) / len(detalles), 2
            )
        
        return {
            'total_eventos': total_eventos,
            'eventos_activos': eventos_activos,
            'eventos_finalizados': eventos_finalizados,
            'ocupacion_promedio': ocupacion_promedio,
            'detalles': detalles,
        }
    
    @staticmethod
    def get_reporte_personal(fecha_inicio=None, fecha_fin=None, usuario_id=None):
        """
        Generar reporte de rendimiento del personal
        """
        # Filtros
        usuarios_filter = Q(rol__in=['VENDEDOR', 'VALIDADOR'])
        
        if usuario_id:
            usuarios_filter &= Q(id=usuario_id)
        
        usuarios = Usuario.objects.filter(usuarios_filter)
        
        total_vendedores = usuarios.filter(rol='VENDEDOR').count()
        total_validadores = usuarios.filter(rol='VALIDADOR').count()
        
        # Detalles por usuario
        detalles = []
        
        for usuario in usuarios:
            if usuario.rol == 'VENDEDOR':
                # Ventas del vendedor
                ventas_filter = Q(vendedor=usuario)
                
                if fecha_inicio:
                    ventas_filter &= Q(fecha_venta__gte=fecha_inicio)
                if fecha_fin:
                    ventas_filter &= Q(fecha_venta__lte=fecha_fin)
                
                ventas_data = Venta.objects.filter(ventas_filter).aggregate(
                    total_ventas=Count('id'),
                    total_ingresos=Coalesce(Sum('total_pagado'), Decimal('0.00'))
                )
                
                detalles.append({
                    'id': usuario.id,
                    'nombre': usuario.get_full_name() or usuario.username,
                    'rol': 'Vendedor',
                    'ventas': ventas_data['total_ventas'],
                    'total': float(ventas_data['total_ingresos']),
                })
            
            elif usuario.rol == 'VALIDADOR':
                # Validaciones del validador
                validaciones_filter = Q(validador=usuario)
                
                if fecha_inicio:
                    validaciones_filter &= Q(fecha_hora_ingreso__gte=fecha_inicio)
                if fecha_fin:
                    validaciones_filter &= Q(fecha_hora_ingreso__lte=fecha_fin)
                
                validaciones_data = Validacion.objects.filter(validaciones_filter).aggregate(
                    total_validaciones=Count('id')
                )
                
                detalles.append({
                    'id': usuario.id,
                    'nombre': usuario.get_full_name() or usuario.username,
                    'rol': 'Validador',
                    'ventas': validaciones_data['total_validaciones'],
                    'total': validaciones_data['total_validaciones'],
                })
        
        return {
            'total_vendedores': total_vendedores,
            'total_validadores': total_validadores,
            'detalles': detalles,
        }
