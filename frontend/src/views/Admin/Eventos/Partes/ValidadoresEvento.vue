<template>
    <div class="space-y-6">
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-xl font-semibold text-gray-900">Validadores Asignados</h3>
                <p class="text-sm text-gray-600 mt-1">
                    Solo los validadores asignados podrán escanear entradas de este evento
                </p>
            </div>
            <button
                @click="modalAgregar = true"
                class="px-4 py-2 bg-[#B3224D] text-white rounded-lg hover:bg-[#8B1A3A] transition-colors"
            >
                + Agregar Validador
            </button>
        </div>

        <!-- Lista de validadores asignados -->
        <div v-if="validadoresAsignados.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Nombre
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Email
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Fecha Asignación
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Estado
                            </th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Acciones
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="validador in validadoresAsignados" :key="validador.id">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 h-10 w-10 bg-[#B3224D] rounded-full flex items-center justify-center">
                                        <span class="text-white font-medium">
                                            {{ validador.nombre_completo?.charAt(0).toUpperCase() }}
                                        </span>
                                    </div>
                                    <div class="ml-4">
                                        <div class="text-sm font-medium text-gray-900">
                                            {{ validador.nombre_completo }}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{ validador.email }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{ formatDate(validador.fecha_asignacion) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span :class="[
                                    'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full',
                                    validador.activo 
                                        ? 'bg-green-100 text-green-800' 
                                        : 'bg-red-100 text-red-800'
                                ]">
                                    {{ validador.activo ? 'Activo' : 'Inactivo' }}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <button
                                    @click="confirmarRemover(validador)"
                                    class="text-red-600 hover:text-red-900"
                                >
                                    Remover
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Estado vacío -->
        <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No hay validadores asignados</h3>
            <p class="mt-1 text-sm text-gray-500">
                Comienza agregando validadores para este evento
            </p>
        </div>

        <!-- Modal: Agregar Validadores -->
        <Teleport to="body">
            <div v-if="modalAgregar" class="fixed inset-0 z-50 overflow-y-auto">
                <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
                    <!-- Overlay -->
                    <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="modalAgregar = false"></div>

                    <!-- Modal -->
                    <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                            <h3 class="text-lg font-medium text-gray-900 mb-4">
                                Seleccionar Validadores
                            </h3>

                            <!-- Loading -->
                            <div v-if="loadingValidadores" class="text-center py-4">
                                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#B3224D] mx-auto"></div>
                                <p class="mt-2 text-sm text-gray-500">Cargando validadores...</p>
                            </div>

                            <!-- Lista de validadores disponibles -->
                            <div v-else class="max-h-96 overflow-y-auto space-y-2">
                                <label
                                    v-for="validador in validadoresDisponibles"
                                    :key="validador.id"
                                    class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                                >
                                    <input
                                        type="checkbox"
                                        :value="validador.id"
                                        v-model="validadoresSeleccionados"
                                        class="h-4 w-4 text-[#B3224D] focus:ring-[#B3224D] border-gray-300 rounded"
                                    />
                                    <div class="ml-3">
                                        <p class="text-sm font-medium text-gray-900">
                                            {{ validador.nombre_completo }}
                                        </p>
                                        <p class="text-xs text-gray-500">
                                            {{ validador.email }}
                                        </p>
                                    </div>
                                </label>

                                <!-- Sin validadores disponibles -->
                                <div v-if="validadoresDisponibles.length === 0" class="text-center py-8">
                                    <p class="text-sm text-gray-500 mb-2">
                                        No hay validadores disponibles para asignar
                                    </p>
                                    <p class="text-xs text-gray-400" v-if="todosLosValidadores.length === 0">
                                        No hay usuarios con rol VALIDADOR en el sistema.<br>
                                        Crea uno desde <router-link to="/admin/trabajadores" class="text-[#B3224D] underline">Gestión de Trabajadores</router-link>
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                            <button
                                @click="asignarValidadores"
                                :disabled="validadoresSeleccionados.length === 0 || isSubmitting"
                                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-[#B3224D] text-base font-medium text-white hover:bg-[#8B1A3A] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#B3224D] sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {{ isSubmitting ? 'Asignando...' : 'Asignar Seleccionados' }}
                            </button>
                            <button
                                @click="modalAgregar = false"
                                :disabled="isSubmitting"
                                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#B3224D] sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { validadoresService } from '@/services/validadoresService';

const props = defineProps({
    eventoId: {
        type: [String, Number],
        required: true
    }
});

const emit = defineEmits(['update', 'error']);

// Estado
const validadoresAsignados = ref([]);
const todosLosValidadores = ref([]);
const loadingValidadores = ref(false);
const isSubmitting = ref(false);
const modalAgregar = ref(false);
const validadoresSeleccionados = ref([]);

// Computed
const validadoresDisponibles = computed(() => {
    const asignadosIds = validadoresAsignados.value.map(v => v.id);
    return todosLosValidadores.value.filter(v => !asignadosIds.includes(v.id));
});

// Métodos
const cargarValidadores = async () => {
    loadingValidadores.value = true;
    try {
        // Cargar todos los validadores del sistema
        const response = await validadoresService.getValidadores();
        todosLosValidadores.value = Array.isArray(response) ? response : response.results || [];
        console.log('Validadores cargados:', todosLosValidadores.value.length);
        
        if (todosLosValidadores.value.length === 0) {
            console.warn('⚠️ No hay usuarios con rol VALIDADOR en el sistema. Crea uno primero en /admin/trabajadores');
        }
    } catch (error) {
        console.error('Error al cargar validadores:', error);
        emit('error', 'Error al cargar la lista de validadores');
    } finally {
        loadingValidadores.value = false;
    }
};

const cargarValidadoresAsignados = async () => {
    try {
        const response = await validadoresService.getValidadoresEvento(props.eventoId);
        validadoresAsignados.value = response.validadores || response || [];
    } catch (error) {
        console.error('Error al cargar validadores asignados:', error);
        // No mostrar error si es 404 (evento sin validadores aún)
        if (error.response?.status !== 404) {
            emit('error', 'Error al cargar validadores asignados');
        }
    }
};

const asignarValidadores = async () => {
    if (validadoresSeleccionados.value.length === 0) return;

    isSubmitting.value = true;
    try {
        await validadoresService.asignarValidadores(props.eventoId, validadoresSeleccionados.value);
        
        // Recargar lista de asignados
        await cargarValidadoresAsignados();
        
        // Limpiar selección y cerrar modal
        validadoresSeleccionados.value = [];
        modalAgregar.value = false;
        
        emit('update', 'Validadores asignados correctamente');
    } catch (error) {
        console.error('Error al asignar validadores:', error);
        emit('error', error.response?.data?.error || 'Error al asignar validadores');
    } finally {
        isSubmitting.value = false;
    }
};

const confirmarRemover = async (validador) => {
    if (!confirm(`¿Está seguro de remover a ${validador.nombre_completo} de este evento?`)) {
        return;
    }

    try {
        await validadoresService.removerValidador(props.eventoId, validador.id);
        await cargarValidadoresAsignados();
        emit('update', 'Validador removido correctamente');
    } catch (error) {
        console.error('Error al remover validador:', error);
        emit('error', 'Error al remover validador');
    }
};

const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
};

// Lifecycle
onMounted(async () => {
    await cargarValidadores();
    await cargarValidadoresAsignados();
});

// Exponer método para recargar desde el padre
defineExpose({
    recargar: cargarValidadoresAsignados
});
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>
