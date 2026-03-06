<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { ventasService } from '@/services/ventasService';

const props = defineProps({
    show: {
        type: Boolean,
        default: false
    },
    eventoSlug: {
        type: String,
        required: true
    }
});

const emit = defineEmits(['active', 'cancelled']);

const queuePosition = ref(0);
const totalInQueue = ref(0);
const estimatedWait = ref(0);
const updateInterval = ref(3000); // Actualizar cada 3 segundos
let intervalId = null;

// Tiempo formateado
const formattedWaitTime = computed(() => {
    if (estimatedWait.value < 60) {
        return `${estimatedWait.value}s`;
    }
    const minutes = Math.floor(estimatedWait.value / 60);
    const seconds = estimatedWait.value % 60;
    return `${minutes}m ${seconds}s`;
});

// Porcentaje de progreso (invertido: más cerca = más progreso)
const progressPercentage = computed(() => {
    if (totalInQueue.value === 0) return 0;
    const progress = ((totalInQueue.value - queuePosition.value) / totalInQueue.value) * 100;
    return Math.max(0, Math.min(100, progress));
});

// Verificar posición en la cola
const checkQueuePosition = async () => {
    try {
        const response = await ventasService.checkQueuePosition(props.eventoSlug);
        
        if (response.status === 'active') {
            // Usuario está activo, puede comprar
            clearInterval(intervalId);
            emit('active');
        } else if (response.status === 'waiting') {
            // Actualizar posición
            queuePosition.value = response.position;
            totalInQueue.value = response.total_in_queue || response.position;
            estimatedWait.value = response.estimated_wait || 0;
        } else if (response.status === 'not_in_queue') {
            // No está en cola, reintentar unirse
            await joinQueue();
        }
    } catch (error) {
        console.error('Error verificando posición:', error);
        // Si hay error, reintentar cada 5 segundos
        updateInterval.value = 5000;
    }
};

// Unirse a la cola
const joinQueue = async () => {
    try {
        const response = await ventasService.checkQueue(props.eventoSlug);
        
        if (response.status === 'active') {
            emit('active');
        } else if (response.status === 'waiting') {
            queuePosition.value = response.position;
            totalInQueue.value = response.total_in_queue || response.position;
            estimatedWait.value = response.estimated_wait || 0;
        }
    } catch (error) {
        console.error('Error uniéndose a la cola:', error);
    }
};

// Cancelar y salir de la cola
const cancelQueue = async () => {
    try {
        await ventasService.leaveQueue(props.eventoSlug);
        clearInterval(intervalId);
        emit('cancelled');
    } catch (error) {
        console.error('Error saliendo de la cola:', error);
        emit('cancelled'); // Emitir de todos modos
    }
};

// Iniciar polling
watch(() => props.show, (newValue) => {
    if (newValue) {
        // Verificar inmediatamente
        checkQueuePosition();
        
        // Iniciar polling
        intervalId = setInterval(checkQueuePosition, updateInterval.value);
    } else {
        // Limpiar intervalo si se oculta
        if (intervalId) {
            clearInterval(intervalId);
        }
    }
});

// Limpiar al desmontar
onUnmounted(() => {
    if (intervalId) {
        clearInterval(intervalId);
    }
});
</script>

<style scoped>
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.animate-spin {
    animation: spin 1s linear infinite;
}
</style>
<template>
    <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
            <!-- Icono animado -->
            <div class="flex justify-center mb-6">
                <div class="relative">
                    <div class="w-24 h-24 border-8 border-[#B3224D] border-t-transparent rounded-full animate-spin"></div>
                    <div class="absolute inset-0 flex items-center justify-center">
                        <svg class="w-12 h-12 text-[#B3224D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
                        </svg>
                    </div>
                </div>
            </div>

            <!-- Título -->
            <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-white mb-2">
                Sala de Espera Virtual
            </h2>
            <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
                Muchas personas están comprando este evento
            </p>

            <!-- Posición en la cola -->
            <div class="bg-gradient-to-r from-[#B3224D] to-[#8d1a3c] rounded-lg p-6 mb-6 text-white">
                <div class="text-center">
                    <p class="text-sm opacity-90 mb-1">Tu posición en la cola</p>
                    <p class="text-5xl font-bold">{{ queuePosition }}</p>
                    <p class="text-sm opacity-90 mt-2">de {{ totalInQueue }} personas</p>
                </div>
            </div>

            <!-- Tiempo estimado -->
            <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 mb-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <svg class="w-5 h-5 text-[#B3224D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <span class="text-sm text-gray-600 dark:text-gray-300">Tiempo estimado:</span>
                    </div>
                    <span class="text-lg font-bold text-[#B3224D]">{{ formattedWaitTime }}</span>
                </div>
            </div>

            <!-- Barra de progreso -->
            <div class="mb-6">
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div class="bg-gradient-to-r from-[#B3224D] to-[#8d1a3c] h-2 rounded-full transition-all duration-500"
                         :style="{ width: progressPercentage + '%' }"></div>
                </div>
                <p class="text-xs text-center text-gray-500 dark:text-gray-400 mt-2">
                    {{ progressPercentage }}% completado
                </p>
            </div>

            <!-- Mensaje informativo -->
            <div class="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
                <div class="flex items-start space-x-3">
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                    </svg>
                    <div class="text-sm text-blue-800 dark:text-blue-200">
                        <p class="font-medium mb-1">¡No cierres esta ventana!</p>
                        <p class="text-xs">Actualizaremos automáticamente cuando sea tu turno</p>
                    </div>
                </div>
            </div>

            <!-- Botón cancelar -->
            <button @click="cancelQueue" 
                    class="w-full py-3 px-4 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition">
                Cancelar y Salir
            </button>

            <!-- Info adicional -->
            <p class="text-xs text-center text-gray-500 dark:text-gray-400 mt-4">
                Actualización automática cada {{ updateInterval / 1000 }} segundos
            </p>
        </div>
    </div>
</template>