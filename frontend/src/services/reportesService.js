/**
 * Reportes Service - Single Responsibility
 * Responsabilidad: Gestionar operaciones de reportes y estadísticas
 */
import api from './api'

export const reportesService = {
  /**
   * Obtener reporte de ventas
   * @param {Object} filtros - Filtros para el reporte
   */
  async getReporteVentas(filtros = {}) {
    const params = {
      fecha_inicio: filtros.fecha_inicio || null,
      fecha_fin: filtros.fecha_fin || null,
      evento_id: filtros.evento_id || null,
    }

    // Remover parámetros nulos
    Object.keys(params).forEach(key => {
      if (params[key] === null) delete params[key]
    })

    const response = await api.get('/reportes/ventas/', { params })
    return response.data
  },

  /**
   * Obtener reporte de validaciones
   */
  async getReporteValidaciones(filtros = {}) {
    const params = {
      fecha_inicio: filtros.fecha_inicio || null,
      fecha_fin: filtros.fecha_fin || null,
      evento_id: filtros.evento_id || null,
    }

    Object.keys(params).forEach(key => {
      if (params[key] === null) delete params[key]
    })

    const response = await api.get('/reportes/validaciones/', { params })
    return response.data
  },

  /**
   * Obtener reporte de eventos
   */
  async getReporteEventos(filtros = {}) {
    const params = {
      fecha_inicio: filtros.fecha_inicio || null,
      fecha_fin: filtros.fecha_fin || null,
    }

    Object.keys(params).forEach(key => {
      if (params[key] === null) delete params[key]
    })

    const response = await api.get('/reportes/eventos/', { params })
    return response.data
  },

  /**
   * Obtener reporte de rendimiento del personal
   */
  async getReportePersonal(filtros = {}) {
    const params = {
      fecha_inicio: filtros.fecha_inicio || null,
      fecha_fin: filtros.fecha_fin || null,
      usuario_id: filtros.usuario_id || null,
    }

    Object.keys(params).forEach(key => {
      if (params[key] === null) delete params[key]
    })

    const response = await api.get('/reportes/personal/', { params })
    return response.data
  },

  /**
   * Obtener dashboard con métricas generales
   */
  async getDashboard(filtros = {}) {
    const params = {
      fecha_inicio: filtros.fecha_inicio || null,
      fecha_fin: filtros.fecha_fin || null,
    }

    Object.keys(params).forEach(key => {
      if (params[key] === null) delete params[key]
    })

    const response = await api.get('/reportes/dashboard/', { params })
    return response.data
  },

  /**
   * Exportar reporte a PDF
   */
  async exportarPDF(tipoReporte, filtros = {}) {
    const response = await api.post(`/reportes/exportar-pdf/${tipoReporte}/`, filtros, {
      responseType: 'blob',
    })
    
    // Crear un link de descarga
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `reporte-${tipoReporte}-${new Date().toISOString().split('T')[0]}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    return response.data
  },

  /**
   * Exportar reporte a Excel
   */
  async exportarExcel(tipoReporte, filtros = {}) {
    const response = await api.post(`/reportes/exportar-excel/${tipoReporte}/`, filtros, {
      responseType: 'blob',
    })
    
    // Crear un link de descarga
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `reporte-${tipoReporte}-${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    return response.data
  },

  /**
   * Obtener métricas en tiempo real
   */
  async getMetricasEnVivo(evento_id = null) {
    const params = evento_id ? { evento_id } : {}
    const response = await api.get('/reportes/metricas-vivo/', { params })
    return response.data
  },

  /**
   * Obtener comparativa entre eventos
   */
  async getComparativaEventos(evento_ids = []) {
    const response = await api.post('/reportes/comparativa-eventos/', {
      evento_ids
    })
    return response.data
  },

  /**
   * Obtener reporte de métodos de pago
   */
  async getReportePagos(filtros = {}) {
    const params = {
      fecha_inicio: filtros.fecha_inicio || null,
      fecha_fin: filtros.fecha_fin || null,
    }

    Object.keys(params).forEach(key => {
      if (params[key] === null) delete params[key]
    })

    const response = await api.get('/reportes/metodos-pago/', { params })
    return response.data
  },

  /**
   * Obtener análisis de zonas más vendidas
   */
  async getAnalisisZonas(evento_id = null) {
    const params = evento_id ? { evento_id } : {}
    const response = await api.get('/reportes/analisis-zonas/', { params })
    return response.data
  }
}

export default reportesService
