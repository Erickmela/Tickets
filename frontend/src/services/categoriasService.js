import api from './api'

export const categoriasService = {
  getCategorias(page = 1, pageSize = 10, search = '') {
    return api.get('/eventos/categorias/', {
      params: { page, page_size: pageSize, search }
    }).then(r => r.data)
  },
  getCategoria(id) {
    return api.get(`/eventos/categorias/${id}/`).then(r => r.data)
  },
  createCategoria(data) {
    return api.post('/eventos/categorias/', data).then(r => r.data)
  },
  updateCategoria(id, data) {
    return api.put(`/eventos/categorias/${id}/`, data).then(r => r.data)
  },
  patchCategoria(id, data) {
    return api.patch(`/eventos/categorias/${id}/`, data).then(r => r.data)
  },
  deleteCategoria(id) {
    return api.delete(`/eventos/categorias/${id}/`).then(r => r.data)
  }
}
