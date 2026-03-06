/**
 * Responsabilidad: Gestionar operaciones de ventas y tickets
 */
import api from './api'

export const ventasService = {
  /**
   * Crear una venta con múltiples tickets
   */
  async crearVenta(ventaData) {
    const response = await api.post('/ventas/crear-venta/', ventaData)
    return response.data
  },

  /**
   * Obtener todas las ventas con paginación
   */
  async getVentas(page = 1, pageSize = 10, search = '') {
    const params = {
      page,
      page_size: pageSize,
    }

    if (search) {
      params.search = search
    }

    const response = await api.get('/ventas/ventas/', { params })
    return response.data
  },

  /**
   * Obtener detalle de una venta
   */
  async getVenta(codigoVenta) {
    const response = await api.get(`/ventas/ventas/${codigoVenta}/`)
    return response.data
  },

  /**
   * Obtener todos los tickets con paginación y filtros
   */
  async getTickets(page = 1, pageSize = 10, search = '', estado = '') {
    const params = {
      page,
      page_size: pageSize,
    }

    if (search) {
      params.search = search
    }

    if (estado) {
      params.estado = estado
    }

    const response = await api.get('/ventas/tickets/', { params })
    return response.data
  },

  /**
   * Obtener detalle de un ticket específico
   */
  async getTicket(ticketId) {
    const response = await api.get(`/ventas/tickets/${ticketId}/`)
    return response.data
  },

  /**
   * Buscar tickets por DNI
   */
  async buscarTicketsPorDNI(dni) {
    const response = await api.get('/ventas/tickets/por_dni/', {
      params: { dni }
    })
    return response.data
  },

  /**
   * Obtener ventas por evento
   */
  async getVentasPorEvento(eventoId) {
    const response = await api.get('/ventas/ventas/', {
      params: { 
        evento_id: eventoId,
        page_size: 1000 // Obtener todas las ventas
      }
    })
    return response.data.results || response.data
  },

  /**
   * Buscar cliente por DNI
   */
  async buscarClientePorDNI(dni) {
    try {
      const response = await api.get('/usuarios/clientes/buscar_por_dni/', {
        params: { dni }
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * Anular una venta
   */
  async anularVenta(codigoVenta, motivo) {
    const response = await api.post(`/ventas/ventas/${codigoVenta}/anular/`, {
      motivo
    })
    return response.data
  },

  // ========== COLA VIRTUAL ==========

  /**
   * Verificar si hay cola y unirse si es necesario
   */
  async checkQueue(eventoSlug) {
    const response = await api.post('/ventas/ventas/check-queue/', {
      evento_slug: eventoSlug
    })
    return response.data
  },

  /**
   * Obtener posición actual en la cola
   */
  async checkQueuePosition(eventoSlug) {
    const response = await api.get('/ventas/ventas/queue-position/', {
      params: { evento_slug: eventoSlug }
    })
    return response.data
  },

  /**
   * Salir de la cola
   */
  async leaveQueue(eventoSlug) {
    const response = await api.post('/ventas/ventas/leave-queue/', {
      evento_slug: eventoSlug
    })
    return response.data
  },

  /**
   * Obtener estadísticas de la cola (solo ADMIN)
   */
  async getQueueStats(eventoSlug) {
    const response = await api.get('/ventas/ventas/queue-stats/', {
      params: { evento_slug: eventoSlug }
    })
    return response.data
  }
}
