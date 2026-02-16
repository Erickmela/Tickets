/**
 * Eventos Store - Aplicando Single Responsibility
 * Responsabilidad: Gestionar el estado de eventos y zonas
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { eventosService } from '@/services/eventosService'

export const useEventosStore = defineStore('eventos', () => {
  // State
  const eventoActivo = ref(null)
  const eventosActivos = ref([])
  const eventos = ref([])
  const zonasDisponibles = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const hayEventoActivo = computed(() => eventoActivo.value !== null)
  const hayEventosActivos = computed(() => eventosActivos.value.length > 0)
  const nombreEventoActivo = computed(() => eventoActivo.value?.nombre)

  // Actions
  async function fetchEventoActivo() {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.getEventoActivo()
      eventoActivo.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'No hay eventos activos'
      eventoActivo.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEventosActivos() {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.getEventosActivos()
      eventosActivos.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'No hay eventos activos'
      eventosActivos.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEventos(page = 1, pageSize = 10, search = '') {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.getEventos(page, pageSize, search)
      eventos.value = data.results || data
      return data
    } catch (err) {
      error.value = 'Error al cargar eventos'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEvento(id) {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.getEvento(id)
      return data
    } catch (err) {
      error.value = 'Error al cargar el evento'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createEvento(eventoData) {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.createEvento(eventoData)
      return data
    } catch (err) {
      error.value = 'Error al crear el evento'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateEvento(id, eventoData) {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.updateEvento(id, eventoData)
      return data
    } catch (err) {
      error.value = 'Error al actualizar el evento'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteEvento(id) {
    loading.value = true
    error.value = null
    try {
      await eventosService.deleteEvento(id)
    } catch (err) {
      error.value = 'Error al eliminar el evento'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchZonasDisponibles(eventoId) {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.getZonasDisponibles(eventoId)
      zonasDisponibles.value = data
      return data
    } catch (err) {
      error.value = 'Error al cargar zonas'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchZonasByEvento(eventoId, page = 1, pageSize = 10, search = '') {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.getZonasByEvento(eventoId, page, pageSize, search)
      return data
    } catch (err) {
      error.value = 'Error al cargar zonas del evento'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createZona(zonaData) {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.createZona(zonaData)
      return data
    } catch (err) {
      error.value = 'Error al crear la zona'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateZona(id, zonaData) {
    loading.value = true
    error.value = null
    try {
      const data = await eventosService.updateZona(id, zonaData)
      return data
    } catch (err) {
      error.value = 'Error al actualizar la zona'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteZona(id) {
    loading.value = true
    error.value = null
    try {
      await eventosService.deleteZona(id)
    } catch (err) {
      error.value = 'Error al eliminar la zona'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function verificarDisponibilidad(zonaId, cantidad) {
    try {
      const data = await eventosService.verificarDisponibilidad(zonaId, cantidad)
      return data
    } catch (err) {
      throw err
    }
  }

  return {
    eventoActivo,
    eventosActivos,
    eventos,
    zonasDisponibles,
    loading,
    error,
    hayEventoActivo,
    hayEventosActivos,
    nombreEventoActivo,
    fetchEventoActivo,
    fetchEventosActivos,
    fetchEventos,
    fetchEvento,
    createEvento,
    updateEvento,
    deleteEvento,
    fetchZonasDisponibles,
    fetchZonasByEvento,
    createZona,
    updateZona,
    deleteZona,
    verificarDisponibilidad
  }
})
