<script setup>
import { ref, onMounted, watch } from 'vue';
import { eventosService } from '@/services/eventosService';
import { Calendar } from 'lucide-vue-next';

const emit = defineEmits(['eventoSeleccionado']);

const eventos = ref([]);
const eventoSeleccionado = ref('');
const loading = ref(true);

const cargarEventos = async () => {
    try {
        loading.value = true;
        const response = await eventosService.getEventos();
        eventos.value = response.results || response;

        // Seleccionar el primer evento activo por defecto
        const eventoActivo = eventos.value.find(e => e.estado === '2') || eventos.value[0];
        if (eventoActivo) {
            eventoSeleccionado.value = eventoActivo.id;
            emit('eventoSeleccionado', eventoActivo);
        }
    } catch (error) {
        console.error('Error al cargar eventos:', error);
    } finally {
        loading.value = false;
    }
};

watch(eventoSeleccionado, (nuevoId) => {
    const evento = eventos.value.find(e => e.id === parseInt(nuevoId));
    if (evento) {
        emit('eventoSeleccionado', evento);
    }
});

onMounted(() => {
    cargarEventos();
});
</script>

<template>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center gap-3 mb-4">
            <Calendar :size="24" :stroke-width="2" class="text-[#B3224D]" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Seleccionar Evento
            </h3>
        </div>

        <div v-if="loading" class="animate-pulse">
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
        </div>

        <div v-else>
            <select v-model="eventoSeleccionado"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent dark:bg-gray-700 dark:text-white text-base">
                <option value="" disabled>Selecciona un evento</option>
                <option v-for="evento in eventos" :key="evento.id" :value="evento.id">
                    {{ evento.nombre }} - {{ new Date(evento.fecha).toLocaleDateString('es-PE') }}
                    <span v-if="evento.estado === '2'">(Activo)</span>
                </option>
            </select>
        </div>
    </div>
</template>
