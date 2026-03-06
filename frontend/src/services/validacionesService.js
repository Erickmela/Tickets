/**
 * Validaciones Service - Aplicando Single Responsibility
 * Responsabilidad: Gestionar validación de tickets en puerta
 */
import api from './api'

export const validacionesService = {
  /**
   * Validar un ticket por su código UUID (escaneo de QR)
   */
  async validarTicket(codigoUUID, observaciones = '', dispositivo = '') {
    const response = await api.post('/validaciones/validar-ticket/', {
      codigo_uuid: codigoUUID,
      observaciones,
      dispositivo
    })
    return response.data
  },

  /**
   * Obtener estadísticas de validaciones
   */
  async getEstadisticas() {
    const response = await api.get('/validaciones/validaciones/estadisticas/')
    return response.data
  }
}
