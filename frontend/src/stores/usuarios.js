/**
 * Usuarios Store - Gestión de Trabajadores y Clientes
 * Responsabilidad: Estado global de usuarios del sistema
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usuariosService } from '@/services/usuariosService'

export const useUsuariosStore = defineStore('usuarios', () => {
  // State
  const trabajadores = ref([])
  const clientes = ref([])
  const trabajadorActual = ref(null)
  const clienteActual = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const totalTrabajadores = computed(() => trabajadores.value.length)
  const totalClientes = computed(() => clientes.value.length)
  const administradores = computed(() => 
    trabajadores.value.filter(t => t.rol === 'ADMIN')
  )
  const vendedores = computed(() => 
    trabajadores.value.filter(t => t.rol === 'VENDEDOR')
  )
  const validadores = computed(() => 
    trabajadores.value.filter(t => t.rol === 'VALIDADOR')
  )

  // ==================== TRABAJADORES ====================

  async function fetchTrabajadores(page = 1, pageSize = 10, search = '', rol = '') {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.getTrabajadores(page, pageSize, search, rol)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cargar trabajadores'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTrabajador(id) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.getTrabajador(id)
      trabajadorActual.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cargar trabajador'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTrabajador(trabajadorData) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.createTrabajador(trabajadorData)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al crear trabajador'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTrabajador(id, trabajadorData) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.updateTrabajador(id, trabajadorData)
      trabajadorActual.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al actualizar trabajador'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteTrabajador(id) {
    loading.value = true
    error.value = null
    try {
      await usuariosService.deleteTrabajador(id)
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al eliminar trabajador'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function toggleTrabajadorActivo(id) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.toggleTrabajadorActivo(id)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cambiar estado'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ==================== CLIENTES ====================

  async function fetchClientes(page = 1, pageSize = 10, search = '') {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.getClientes(page, pageSize, search)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cargar clientes'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCliente(id) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.getCliente(id)
      clienteActual.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cargar cliente'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createCliente(clienteData) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.createCliente(clienteData)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al crear cliente'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateCliente(id, clienteData) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.updateCliente(id, clienteData)
      clienteActual.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al actualizar cliente'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteCliente(id) {
    loading.value = true
    error.value = null
    try {
      await usuariosService.deleteCliente(id)
      return true
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al eliminar cliente'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateMiPerfil(perfilData) {
    loading.value = true
    error.value = null
    try {
      const data = await usuariosService.updateMiPerfil(perfilData)
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al actualizar perfil'
      throw err
    } finally {
      loading.value = false
    }
  }

  function $reset() {
    trabajadores.value = []
    clientes.value = []
    trabajadorActual.value = null
    clienteActual.value = null
    loading.value = false
    error.value = null
  }

  return {
    // State
    trabajadores,
    clientes,
    trabajadorActual,
    clienteActual,
    loading,
    error,
    
    // Getters
    totalTrabajadores,
    totalClientes,
    administradores,
    vendedores,
    validadores,
    
    // Actions Trabajadores
    fetchTrabajadores,
    fetchTrabajador,
    createTrabajador,
    updateTrabajador,
    deleteTrabajador,
    toggleTrabajadorActivo,
    
    // Actions Clientes
    fetchClientes,
    fetchCliente,
    createCliente,
    updateCliente,
    deleteCliente,
    updateMiPerfil,
    
    // Reset
    $reset
  }
})

export default useUsuariosStore
