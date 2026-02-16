/**
 * Ventas Store - Aplicando Single Responsibility
 * Responsabilidad: Gestionar el estado de ventas
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ventasService } from '@/services/ventasService'

export const useVentasStore = defineStore('ventas', () => {
  // State
  const ventas = ref([])
  const ventaActual = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function crearVenta(ventaData) {
    loading.value = true
    error.value = null
    try {
      const data = await ventasService.crearVenta(ventaData)
      ventas.value.unshift(data.venta)
      return data
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al crear la venta'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchVentas(page = 1, pageSize = 10, search = '') {
    loading.value = true
    error.value = null
    try {
      const data = await ventasService.getVentas(page, pageSize, search)
      ventas.value = data.results || data
      return data
    } catch (err) {
      error.value = 'Error al cargar ventas'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchMisVentas(page = 1, pageSize = 10) {
    loading.value = true
    error.value = null
    try {
      const data = await ventasService.getMisVentas(page, pageSize)
      ventas.value = data.results || data
      return data
    } catch (err) {
      error.value = 'Error al cargar ventas'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchVenta(ventaId) {
    loading.value = true
    error.value = null
    try {
      const data = await ventasService.getVenta(ventaId)
      ventaActual.value = data
      return data
    } catch (err) {
      error.value = 'Error al cargar la venta'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function buscarClientePorDNI(dni) {
    try {
      const data = await ventasService.buscarClientePorDNI(dni)
      return data
    } catch (err) {
      throw err
    }
  }

  async function anularVenta(ventaId, motivo) {
    loading.value = true
    error.value = null
    try {
      const data = await ventasService.anularVenta(ventaId, motivo)
      // Actualizar la venta en la lista
      const index = ventas.value.findIndex(v => v.id === ventaId)
      if (index !== -1) {
        ventas.value[index].activo = false
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al anular la venta'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    ventas,
    ventaActual,
    loading,
    error,
    crearVenta,
    fetchVentas,
    fetchMisVentas,
    fetchVenta,
    buscarClientePorDNI,
    anularVenta
  }
})
