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
  async getEvento(id) {
    const response = await api.get(`/eventos/eventos/${id}/`)
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
  async updateEvento(id, eventoData) {
    const response = await api.put(`/eventos/eventos/${id}/`, eventoData)
    return response.data
  },

  /**
   * Eliminar un evento
   */
  async deleteEvento(id) {
    const response = await api.delete(`/eventos/eventos/${id}/`)
    return response.data
  },

  /**
   * Obtener el evento activo (endpoint legacy)
   */
  async getEventoActivo() {
    const response = await api.get('/eventos/eventos/evento_activo/')
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
   * Obtener estadísticas de un evento
   */
  async getEstadisticasEvento(eventoId) {
    const response = await api.get(`/eventos/eventos/${eventoId}/estadisticas/`)
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
   * @param {number} eventoId - ID del evento
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
  async updateZona(id, zonaData) {
    const response = await api.put(`/eventos/zonas/${id}/`, zonaData)
    return response.data
  },

  /**
   * Eliminar una zona
   */
  async deleteZona(id) {
    const response = await api.delete(`/eventos/zonas/${id}/`)
    return response.data
  },

  /**
   * Verificar disponibilidad de una zona
   */
  async verificarDisponibilidad(zonaId, cantidad) {
    const response = await api.get(`/eventos/zonas/${zonaId}/disponibilidad/`, {
      params: { cantidad }
    })
    return response.data
  }
}
