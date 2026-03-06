import api from '@/services/api';
import { setCartCount } from "@/Helpers/cartState";

/**
 * Agregar un evento al carrito
 * @param {string|number} eventoId - ID del evento a agregar
 * @returns {Promise<{success: boolean, message: string}>}
 */
export async function agregarEventoAlCarrito(eventoId) {
    try {
        const response = await api.post('/ventas/carrito/', {
            evento_id: eventoId
        });

        if (response.data.success) {
            if (response.data.count !== undefined) {
                setCartCount(response.data.count);
            }
            return { success: true, message: response.data.message || 'Evento agregado al carrito' };
        } else {
            console.error(response.data.message);
            return { success: false, message: response.data.message || 'Error al agregar al carrito' };
        }
    } catch (error) {
        let message = 'Error desconocido al agregar el evento.';
        if (error.response && error.response.data && error.response.data.message) {
            message = error.response.data.message;
        }
        console.error('Error agregando evento:', error);
        return { success: false, message: message };
    }
}

/**
 * Legacy: Agregar curso al carrito (mantener compatibilidad)
 */
export async function agregarCursoAlCarrito(cur_id) {
    try {
        const response = await api.post('/carrito/store', {
            cur_id: cur_id
        });

        if (response.data.success) {
            if (response.data.count !== undefined) {
                setCartCount(response.data.count);
            }
            return { success: true, message: response.data.message };
        } else {
            console.error(response.data.message);
            return { success: false, message: response.data.message };
        }
    } catch (error) {
        let message = 'Error desconocido al agregar el curso.';
        if (error.response && error.response.data && error.response.data.message) {
            message = error.response.data.message;
        }
        return { success: false, message: message };
    }
}
