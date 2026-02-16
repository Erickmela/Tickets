/**
 * Usuarios Service - Gestión de Usuarios y Clientes
 * Responsabilidad: Operaciones API para trabajadores y clientes
 */
import api from './api'

export const usuariosService = {
  // ==================== TRABAJADORES (Usuario model) ====================
  
  /**
   * Obtener todos los trabajadores (Admin, Vendedor, Validador)
   */
  async getTrabajadores(page = 1, pageSize = 10, search = '', rol = '') {
    const response = await api.get('/usuarios/usuarios/', {
      params: {
        page,
        page_size: pageSize,
        search,
        rol
      }
    })
    return response.data
  },

  /**
   * Obtener un trabajador específico
   */
  async getTrabajador(id) {
    const response = await api.get(`/usuarios/usuarios/${id}/`)
    return response.data
  },

  /**
   * Crear un nuevo trabajador
   */
  async createTrabajador(trabajadorData) {
    const response = await api.post('/usuarios/usuarios/', trabajadorData)
    return response.data
  },

  /**
   * Actualizar un trabajador
   */
  async updateTrabajador(id, trabajadorData) {
    const response = await api.put(`/usuarios/usuarios/${id}/`, trabajadorData)
    return response.data
  },

  /**
   * Eliminar un trabajador
   */
  async deleteTrabajador(id) {
    const response = await api.delete(`/usuarios/usuarios/${id}/`)
    return response.data
  },

  /**
   * Alternar estado activo de trabajador
   */
  async toggleTrabajadorActivo(id) {
    const response = await api.post(`/usuarios/usuarios/${id}/toggle_activo/`)
    return response.data
  },

  // ==================== CLIENTES (PerfilCliente model) ====================
  
  /**
   * Obtener todos los clientes
   */
  async getClientes(page = 1, pageSize = 10, search = '') {
    const response = await api.get('/usuarios/clientes/', {
      params: {
        page,
        page_size: pageSize,
        search
      }
    })
    return response.data
  },

  /**
   * Obtener un cliente específico
   */
  async getCliente(id) {
    const response = await api.get(`/usuarios/clientes/${id}/`)
    return response.data
  },

  /**
   * Crear un nuevo cliente
   */
  async createCliente(clienteData) {
    const response = await api.post('/usuarios/clientes/', clienteData)
    return response.data
  },

  /**
   * Actualizar un cliente
   */
  async updateCliente(id, clienteData) {
    const response = await api.put(`/usuarios/clientes/${id}/`, clienteData)
    return response.data
  },

  /**
   * Eliminar un cliente
   */
  async deleteCliente(id) {
    const response = await api.delete(`/usuarios/clientes/${id}/`)
    return response.data
  },

  /**
   * Actualizar perfil del cliente autenticado
   */
  async updateMiPerfil(perfilData) {
    const response = await api.put('/usuarios/clientes/mi_perfil/', perfilData)
    return response.data
  }
}

export default usuariosService
