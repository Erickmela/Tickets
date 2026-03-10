/**
 * Servicio para gestión de validadores por evento
 */
import api from './api';

export const validadoresService = {
    /**
     * Obtener todos los validadores del sistema
     */
    async getValidadores() {
        try {
            const response = await api.get('/usuarios/usuarios/', {
                params: { rol: 'VALIDADOR' }
            });
            return response.data;
        } catch (error) {
            console.error('Error al obtener validadores:', error);
            throw error;
        }
    },

    /**
     * Obtener validadores asignados a un evento específico
     */
    async getValidadoresEvento(eventoId) {
        try {
            const response = await api.get(`/eventos/eventos/${eventoId}/validadores/`);
            return response.data;
        } catch (error) {
            console.error('Error al obtener validadores del evento:', error);
            throw error;
        }
    },

    /**
     * Asignar validadores a un evento
     */
    async asignarValidadores(eventoId, validadoresIds) {
        try {
            const response = await api.post(`/eventos/eventos/${eventoId}/asignar-validadores/`, {
                validadores: validadoresIds
            });
            return response.data;
        } catch (error) {
            console.error('Error al asignar validadores:', error);
            throw error;
        }
    },

    /**
     * Remover un validador de un evento
     */
    async removerValidador(eventoId, validadorId) {
        try {
            const response = await api.delete(`/eventos/eventos/${eventoId}/validadores/${validadorId}/`);
            return response.data;
        } catch (error) {
            console.error('Error al remover validador:', error);
            throw error;
        }
    }
};
