/**
 * Auth Service - Aplicando Single Responsibility
 * Responsabilidad: Gestionar autenticación y autorización
 */
import api from './api'

export const authService = {
  /**
   * Iniciar sesión
   */
  async login(username, password) {
    const response = await api.post('/usuarios/login/', {
      username,
      password
    })
    return response.data
  },

  /**
   * Cerrar sesión
   */
  async logout() {
    const response = await api.post('/usuarios/logout/')
    return response.data
  },

  /**
   * Obtener perfil del usuario actual
   */
  async getCurrentUser() {
    const response = await api.get('/usuarios/usuarios/me/')
    return response.data
  },

  /**
   * Verificar permisos del usuario
   */
  hasPermission(user, permission) {
    const rolePermissions = {
      ADMIN: ['crear_usuario', 'ver_reportes', 'anular_tickets', 'crear_eventos', 'crear_ventas', 'validar_tickets'],
      VENDEDOR: ['crear_ventas', 'ver_ventas'],
      VALIDADOR: ['validar_tickets', 'ver_validaciones']
    }
    return rolePermissions[user.rol]?.includes(permission) || false
  }
}
