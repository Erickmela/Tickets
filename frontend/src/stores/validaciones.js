/**
 * Validaciones Store - Aplicando Single Responsibility
 * Responsabilidad: Gestionar el estado de validaciones
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { validacionesService } from '@/services/validacionesService'

export const useValidacionesStore = defineStore('validaciones', () => {
  // State
  const validaciones = ref([])
  const ultimaValidacion = ref(null)
  const estadisticas = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function validarTicket(codigoUUID, observaciones = '') {
    loading.value = true
    error.value = null
    try {
      const dispositivo = getDeviceInfo()
      const data = await validacionesService.validarTicket(
        codigoUUID,
        observaciones,
        dispositivo
      )
      ultimaValidacion.value = data
      if (data.success) {
        validaciones.value.unshift(data)
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al validar ticket'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchValidaciones() {
    loading.value = true
    error.value = null
    try {
      const data = await validacionesService.getValidaciones()
      validaciones.value = data
      return data
    } catch (err) {
      error.value = 'Error al cargar validaciones'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchMisValidaciones() {
    loading.value = true
    error.value = null
    try {
      const data = await validacionesService.getMisValidaciones()
      validaciones.value = data
      return data
    } catch (err) {
      error.value = 'Error al cargar validaciones'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEstadisticas() {
    loading.value = true
    error.value = null
    try {
      const data = await validacionesService.getEstadisticas()
      estadisticas.value = data
      return data
    } catch (err) {
      error.value = 'Error al cargar estadísticas'
      throw err
    } finally {
      loading.value = false
    }
  }

  function getDeviceInfo() {
    return `${navigator.userAgent.substring(0, 100)}`
  }

  function limpiarUltimaValidacion() {
    ultimaValidacion.value = null
  }

  return {
    validaciones,
    ultimaValidacion,
    estadisticas,
    loading,
    error,
    validarTicket,
    fetchValidaciones,
    fetchMisValidaciones,
    fetchEstadisticas,
    limpiarUltimaValidacion
  }
})
