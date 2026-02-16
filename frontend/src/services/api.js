/**
 * API Client - Aplicando Dependency Inversion
 * Cliente HTTP centralizado para todas las peticiones
 */
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Interceptor para configurar headers según el tipo de datos
apiClient.interceptors.request.use(
  (config) => {
    // Si es FormData, permitir que axios configure automáticamente el Content-Type
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores globalmente
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Sesión expirada o no autenticado
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      // Redirigir al home en lugar del login
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/registro')) {
        window.location.href = '/'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
