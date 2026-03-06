/**
 * Servicio de MercadoPago
 * Gestiona la integración con MercadoPago Checkout Pro
 */
import apiClient from './api'

export const mercadoPagoService = {
  /**
   * Sincronizar carrito del localStorage con el backend
   * @param {Array} items - Items del carrito en formato localStorage
   * @returns {Promise} Datos del carrito creado
   */
  async sincronizarCarrito(items) {
    try {
      // Transformar items del formato localStorage al formato backend
      const itemsBackend = items.flatMap(item =>
        item.zonas.map(zona => ({
          presentacion_id: item.presentacionId,
          zona_id: zona.id,
          cantidad: zona.cantidad
        }))
      )

      const response = await apiClient.post('/ventas/carritos/sincronizar/', {
        items: itemsBackend
      })
      return response.data
    } catch (error) {
      console.error('Error sincronizando carrito:', error)
      throw error
    }
  },

  /**
   * Crear preferencia de pago
   * @param {number|null} carritoId - ID del carrito (opcional)
   * @returns {Promise} Datos de la preferencia con init_point
   */
  async crearPreferencia(carritoId = null) {
    try {
      const response = await apiClient.post('/ventas/mercadopago/create_preference/', {
        carrito_id: carritoId
      })
      return response.data
    } catch (error) {
      console.error('Error creando preferencia de MercadoPago:', error)
      throw error
    }
  },

  /**
   * Consultar estado de un pago
   * @param {string} paymentId - ID del pago de MercadoPago
   * @returns {Promise} Estado del pago
   */
  async consultarEstadoPago(paymentId) {
    try {
      const response = await apiClient.get('/ventas/mercadopago/payment_status/', {
        params: { payment_id: paymentId }
      })
      return response.data
    } catch (error) {
      console.error('Error consultando estado de pago:', error)
      throw error
    }
  },

  /**
   * Inicializar SDK de MercadoPago
   * @param {string} publicKey - Public Key de MercadoPago
   * @returns {object} Instancia de MercadoPago
   */
  inicializarSDK(publicKey) {
    if (typeof window.MercadoPago === 'undefined') {
      console.error('SDK de MercadoPago no está cargado')
      return null
    }
    
    try {
      const mp = new window.MercadoPago(publicKey, {
        locale: 'es-PE'
      })
      return mp
    } catch (error) {
      console.error('Error inicializando SDK de MercadoPago:', error)
      return null
    }
  },

  /**
   * Renderizar botón de pago de MercadoPago
   * @param {object} mp - Instancia de MercadoPago
   * @param {string} preferenceId - ID de la preferencia creada
   * @param {string} containerId - ID del contenedor donde renderizar el botón
   */
  renderizarBotonPago(mp, preferenceId, containerId = 'mercadopago-button') {
    if (!mp || !preferenceId) {
      console.error('MP o preferenceId no están definidos')
      return
    }

    try {
      mp.checkout({
        preference: {
          id: preferenceId
        },
        render: {
          container: `#${containerId}`,
          label: 'Pagar con MercadoPago'
        }
      })
    } catch (error) {
      console.error('Error renderizando botón de MercadoPago:', error)
    }
  }
}

export default mercadoPagoService
