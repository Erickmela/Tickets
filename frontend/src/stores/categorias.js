import { defineStore } from 'pinia'
import { ref } from 'vue'
import { categoriasService } from '@/services/categoriasService'

export const useCategoriasStore = defineStore('categorias', () => {
  const categorias = ref([])
  const categoriaActual = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchCategorias(page = 1, pageSize = 10, search = '') {
    loading.value = true
    error.value = null
    try {
      const data = await categoriasService.getCategorias(page, pageSize, search)
      categorias.value = data.results || []
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cargar categorías'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCategoria(id) {
    loading.value = true
    error.value = null
    try {
      const data = await categoriasService.getCategoria(id)
      categoriaActual.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al cargar categoría'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createCategoria(data) {
    loading.value = true
    error.value = null
    try {
      const res = await categoriasService.createCategoria(data)
      return res
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al crear categoría'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateCategoria(id, data) {
    loading.value = true
    error.value = null
    try {
      const res = await categoriasService.updateCategoria(id, data)
      return res
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al actualizar categoría'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function patchCategoria(id, data) {
    loading.value = true
    error.value = null
    try {
      const res = await categoriasService.patchCategoria(id, data)
      return res
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al actualizar categoría'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteCategoria(id) {
    loading.value = true
    error.value = null
    try {
      const res = await categoriasService.deleteCategoria(id)
      return res
    } catch (err) {
      error.value = err.response?.data?.message || 'Error al eliminar categoría'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    categorias,
    categoriaActual,
    loading,
    error,
    fetchCategorias,
    fetchCategoria,
    createCategoria,
    updateCategoria,
    patchCategoria,
    deleteCategoria
  }
})
