/**
 * Reportes Store - State Management
 * Responsabilidad: Gestionar estado de reportes y estadísticas
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import reportesService from '@/services/reportesService'

export const useReportesStore = defineStore('reportes', () => {
  // State
  const reporteActual = ref(null)
  const dashboard = ref({
    total_ventas: 0,
    total_tickets: 0,
    total_validados: 0,
    ingresos_totales: 0,
  })
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const tasaValidacion = computed(() => {
    if (dashboard.value.total_tickets === 0) return 0
    return ((dashboard.value.total_validados / dashboard.value.total_tickets) * 100).toFixed(1)
  })

  const tasaOcupacion = computed(() => {
    // Este cálculo dependerá de tener el total de capacidad disponible
    // Por ahora retornamos 0
    return 0
  })

  // Actions
  /**
   * Cargar dashboard con métricas generales
   */
  const fetchDashboard = async (filtros = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await reportesService.getDashboard(filtros)
      dashboard.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cargar dashboard'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Generar reporte según tipo
   */
  const generarReporte = async (tipo, filtros = {}) => {
    loading.value = true
    error.value = null
    
    try {
      let data
      
      switch (tipo) {
        case 'ventas':
          data = await reportesService.getReporteVentas(filtros)
          break
        case 'validaciones':
          data = await reportesService.getReporteValidaciones(filtros)
          break
        case 'eventos':
          data = await reportesService.getReporteEventos(filtros)
          break
        case 'personal':
          data = await reportesService.getReportePersonal(filtros)
          break
        default:
          throw new Error('Tipo de reporte no válido')
      }
      
      reporteActual.value = {
        tipo,
        filtros,
        data,
        fecha_generacion: new Date()
      }
      
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al generar reporte'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Exportar reporte actual
   */
  const exportarReporte = async (formato = 'pdf') => {
    if (!reporteActual.value) {
      throw new Error('No hay reporte para exportar')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const { tipo, filtros } = reporteActual.value
      
      if (formato === 'pdf') {
        await reportesService.exportarPDF(tipo, filtros)
      } else if (formato === 'excel') {
        await reportesService.exportarExcel(tipo, filtros)
      } else {
        throw new Error('Formato no válido')
      }
      
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al exportar reporte'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Obtener métricas en tiempo real
   */
  const fetchMetricasEnVivo = async (evento_id = null) => {
    try {
      const data = await reportesService.getMetricasEnVivo(evento_id)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al obtener métricas'
      throw err
    }
  }

  /**
   * Comparar eventos
   */
  const compararEventos = async (evento_ids) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await reportesService.getComparativaEventos(evento_ids)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al comparar eventos'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Obtener análisis de zonas
   */
  const fetchAnalisisZonas = async (evento_id = null) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await reportesService.getAnalisisZonas(evento_id)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al obtener análisis de zonas'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Limpiar reporte actual
   */
  const limpiarReporte = () => {
    reporteActual.value = null
    error.value = null
  }

  /**
   * Reset completo del store
   */
  const resetStore = () => {
    reporteActual.value = null
    dashboard.value = {
      total_ventas: 0,
      total_tickets: 0,
      total_validados: 0,
      ingresos_totales: 0,
    }
    loading.value = false
    error.value = null
  }

  return {
    // State
    reporteActual,
    dashboard,
    loading,
    error,
    
    // Getters
    tasaValidacion,
    tasaOcupacion,
    
    // Actions
    fetchDashboard,
    generarReporte,
    exportarReporte,
    fetchMetricasEnVivo,
    compararEventos,
    fetchAnalisisZonas,
    limpiarReporte,
    resetStore,
  }
})
