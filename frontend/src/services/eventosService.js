/**
 * Eventos Service - Aplicando Single Responsibility
 * Responsabilidad: Gestionar operaciones relacionadas con eventos y zonas
 */
import api from './api'

export const eventosService = {
  /**
   * Obtener todos los eventos (con paginación)
   */
  async getEventos(page = 1, pageSize = 10, search = '') {
    const response = await api.get('/eventos/eventos/', {
      params: {
        page,
        page_size: pageSize,
        search
      }
    })
    return response.data
  },

  /**
   * Obtener un evento específico
   */
  async getEvento(slug) {
    const response = await api.get(`/eventos/eventos/${slug}/`)
    return response.data
  },

  /**
   * Crear un nuevo evento
   */
  async createEvento(eventoData) {
    const response = await api.post('/eventos/eventos/', eventoData)
    return response.data
  },

  /**
   * Actualizar un evento
   */
  async updateEvento(slug, eventoData) {
    const response = await api.put(`/eventos/eventos/${slug}/`, eventoData)
    return response.data
  },

  /**
   * Eliminar un evento
   */
  async deleteEvento(slug) {
    const response = await api.delete(`/eventos/eventos/${slug}/`)
    return response.data
  },

  /**
   * Obtener todos los eventos activos
   */
  async getEventosActivos() {
    const response = await api.get('/eventos/eventos/eventos_activos/')
    return response.data
  },

  /**
   * Obtener eventos para landing page (optimizado)
   * Solo retorna campos esenciales para las tarjetas de eventos
   */
  async getEventosLanding() {
    const response = await api.get('/eventos/eventos/eventos-landing/')
    return response.data
  },

  /**
   * Obtener eventos para select (solo id, encoded_id, nombre)
   * Optimizado para formularios y dropdowns
   */
  async getEventosSelect() {
    const response = await api.get('/eventos/eventos/select/')
    return response.data
  },

  /**
   * Obtener estadísticas de un evento
   */
  async getEstadisticasEvento(eventoSlug) {
    const response = await api.get(`/eventos/eventos/${eventoSlug}/estadisticas/`)
    return response.data
  },

  /**
   * Obtener zonas de un evento (con paginación)
   */
  async getZonasByEvento(eventoId, page = 1, pageSize = 10, search = '') {
    const response = await api.get('/eventos/zonas/', {
      params: {
        evento_id: eventoId,
        page,
        page_size: pageSize,
        search
      }
    })
    return response.data
  },

  /**
   * Obtener zonas disponibles de un evento específico
   */
  async getZonasDisponibles(eventoId) {
    const response = await api.get('/eventos/zonas/zonas_disponibles/', {
      params: { evento_id: eventoId }
    })
    return response.data
  },

  /**
   * Crear una nueva zona
   */
  async createZona(zonaData) {
    const response = await api.post('/eventos/zonas/', zonaData)
    return response.data
  },

  /**
   * Actualizar una zona
   */
  async updateZona(codigo, zonaData) {
    const response = await api.put(`/eventos/zonas/${codigo}/`, zonaData)
    return response.data
  },

  /**
   * Eliminar una zona
   */
  async deleteZona(codigo) {
    const response = await api.delete(`/eventos/zonas/${codigo}/`)
    return response.data
  },

  /**
   * Obtener evolución de ventas de los últimos días
   */
  async getEvolucionVentas(eventoSlug, dias = 7) {
    const response = await api.get(`/eventos/eventos/${eventoSlug}/evolucion_ventas/`, {
      params: { dias }
    })
    return response.data
  },

  /**
   * Obtener todos los tickets del evento para generar reporte
   */
  async getTicketsReporte(eventoSlug) {
    const response = await api.get(`/eventos/eventos/${eventoSlug}/tickets_reporte/`)
    return response.data
  }
}
