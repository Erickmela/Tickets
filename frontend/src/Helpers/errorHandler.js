/**
 * Error Handler - Utilidades para manejo de errores de API
 * Responsabilidad: Limpiar y formatear mensajes de error del backend
 */

/**
 * Limpia y formatea mensajes de error del backend
 * Elimina corchetes, comillas y formatos de arrays de Python/Django
 * 
 * @param {*} errorData - Datos del error (puede ser string, object, array)
 * @returns {string} - Mensaje de error limpio y legible
 */
export const limpiarMensajeError = (errorData) => {
    if (!errorData) return 'Error desconocido';
    
    let mensaje = errorData;
    
    // Si es un objeto, intentar extraer el mensaje
    if (typeof errorData === 'object' && !Array.isArray(errorData)) {
        mensaje = errorData.error || errorData.message || errorData.detail || JSON.stringify(errorData);
    }
    
    // Si es un array, tomar el primer elemento
    if (Array.isArray(errorData)) {
        mensaje = errorData[0] || 'Error desconocido';
    }
    
    // Convertir a string si no lo es
    mensaje = String(mensaje);
    
    // Limpiar corchetes y comillas de arrays/listas de Python
    mensaje = mensaje
        .replace(/^\["|"\]$/g, '')  // Remover [" al inicio y "] al final
        .replace(/\['|'\]/g, '')     // Remover [' y ']
        .replace(/\\'/g, "'")        // Reemplazar \' por '
        .replace(/\[|\]/g, '')       // Remover corchetes restantes
        .replace(/^"|"$/g, '')       // Remover comillas al inicio y final
        .trim();
    
    return mensaje;
};

/**
 * Extrae el mensaje de error de una respuesta de Axios
 * 
 * @param {Error} error - Error de Axios
 * @param {string} defaultMessage - Mensaje por defecto si no se puede extraer
 * @returns {string} - Mensaje de error formateado
 */
export const extraerMensajeError = (error, defaultMessage = 'Error en la operación') => {
    if (!error.response) {
        // Error de red o sin respuesta del servidor
        return error.message || 'Error de conexión con el servidor';
    }
    
    const data = error.response.data;
    
    // Intentar diferentes formatos de respuesta del backend
    const rawError = data?.error || data?.message || data?.detail || data;
    
    return limpiarMensajeError(rawError) || defaultMessage;
};

/**
 * Extrae errores de validación de formulario del backend
 * 
 * @param {Error} error - Error de Axios
 * @returns {Object} - Objeto con errores por campo
 */
export const extraerErroresValidacion = (error) => {
    if (!error.response?.data) return {};
    
    const data = error.response.data;
    
    // Si hay un objeto 'errors' con los campos
    if (data.errors && typeof data.errors === 'object') {
        const erroresLimpios = {};
        for (const [campo, mensaje] of Object.entries(data.errors)) {
            erroresLimpios[campo] = limpiarMensajeError(mensaje);
        }
        return erroresLimpios;
    }
    
    // Si el data completo es un objeto con campos de error
    if (typeof data === 'object' && !data.error && !data.message) {
        const erroresLimpios = {};
        for (const [campo, mensaje] of Object.entries(data)) {
            if (Array.isArray(mensaje)) {
                erroresLimpios[campo] = limpiarMensajeError(mensaje[0]);
            } else {
                erroresLimpios[campo] = limpiarMensajeError(mensaje);
            }
        }
        return erroresLimpios;
    }
    
    return {};
};

/**
 * Maneja un error de API de forma completa
 * Retorna un objeto con el mensaje y los errores de validación
 * 
 * @param {Error} error - Error de Axios
 * @param {string} defaultMessage - Mensaje por defecto
 * @returns {Object} - { mensaje: string, errores: Object }
 */
export const manejarErrorAPI = (error, defaultMessage = 'Error en la operación') => {
    return {
        mensaje: extraerMensajeError(error, defaultMessage),
        errores: extraerErroresValidacion(error),
        tieneErroresValidacion: Object.keys(extraerErroresValidacion(error)).length > 0
    };
};
