/**
 * Auth Store - Aplicando Single Responsibility
 * Responsabilidad: Gestionar el estado de autenticación
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => user.value !== null)
  const userRole = computed(() => user.value?.rol)
  const userName = computed(() => user.value?.nombre_completo)

  // Actions
  async function login(username, password) {
    loading.value = true
    error.value = null
    try {
      // Limpiar sesión anterior
      localStorage.removeItem('user')
      user.value = null
      
      const data = await authService.login(username, password)
      user.value = data.user
      localStorage.setItem('user', JSON.stringify(data.user))
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al iniciar sesión'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      await authService.logout()
    } catch (err) {
      console.error('Error al cerrar sesión:', err)
    } finally {
      // Limpiar todo el estado
      user.value = null
      localStorage.removeItem('user')
      localStorage.removeItem('token') // Por si acaso quedó algo
      loading.value = false
    }
  }

  async function fetchCurrentUser() {
    loading.value = true
    try {
      const data = await authService.getCurrentUser()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
    } catch (err) {
      user.value = null
      localStorage.removeItem('user')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function initializeAuth() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
        // Verificar que la sesión siga válida
        try {
          await fetchCurrentUser()
        } catch (err) {
          // Si la sesión expiró, limpiar todo
          user.value = null
          localStorage.removeItem('user')
        }
      } catch (e) {
        localStorage.removeItem('user')
      }
    }
  }

  async function refreshUser() {
    try {
      await fetchCurrentUser()
      return user.value
    } catch (err) {
      console.error('Error al refrescar usuario:', err)
      throw err
    }
  }

  function hasPermission(permission) {
    if (!user.value) return false
    return authService.hasPermission(user.value, permission)
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    userRole,
    userName,
    login,
    logout,
    fetchCurrentUser,
    initializeAuth,
    refreshUser,
    hasPermission
  }
})
