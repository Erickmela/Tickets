<script setup>
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import { Music, Trophy, Drama, Mic, Tent, Utensils, PartyPopper, Sparkles, Calendar, MapPin } from 'lucide-vue-next';
import ButtonPrimary from '@/components/Buttons/ButtonPrimary.vue';
import { eventosService } from '@/services/eventosService';

const eventosDestacados = ref([]);
const loading = ref(true);

// Mapeo de categorías a iconos de Lucide
const categoriaIconos = {
    'Música': Music,
    'Musica': Music,
    'Deportes': Trophy,
    'Teatro': Drama,
    'Conferencias': Mic,
    'Festivales': Tent,
    'Gastronomía': Utensils,
    'Gastronomia': Utensils,
    'Infantiles': PartyPopper,
    'Otros': Sparkles
};

onMounted(async () => {
    try {
        // Cargar eventos activos desde la API
        const eventos = await eventosService.getEventosActivos();
        
        // Tomar solo los primeros 4 eventos para destacados
        eventosDestacados.value = eventos.slice(0, 4).map(evento => ({
            ...evento,
            icono: categoriaIconos[evento.categoria] || Sparkles,
            precioMinimo: obtenerPrecioMinimo(evento)
        }));
    } catch (error) {
        if (error.response?.status === 403) {
            console.warn('Acceso denegado a eventos. Reinicia el servidor backend.');
        } else if (error.response?.status === 404) {
            console.info('No hay eventos activos disponibles.');
        } else {
            console.error('Error cargando eventos:', error.message);
        }
        eventosDestacados.value = [];
    } finally {
        loading.value = false;
    }
});

const obtenerPrecioMinimo = (evento) => {
    if (evento.zonas && evento.zonas.length > 0) {
        const precioMin = Math.min(...evento.zonas.map(z => parseFloat(z.precio)));
        return `Desde S/ ${precioMin.toFixed(2)}`;
    }
    return 'Consultar precio';
};

const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
};
</script>

<template>
    <section class="py-16 bg-gray-50 dark:bg-gray-800">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-12">
                <h2 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                    Eventos Destacados
                </h2>
                <p class="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                    Los eventos más populares y próximos
                </p>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div v-for="i in 4" :key="i" class="bg-white dark:bg-gray-900 rounded-2xl p-4 animate-pulse">
                    <div class="h-48 bg-gray-200 dark:bg-gray-700 rounded-xl mb-4"></div>
                    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                </div>
            </div>

            <!-- Eventos Grid -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div 
                    v-for="evento in eventosDestacados" 
                    :key="evento.id"
                    class="group bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all hover:-translate-y-1"
                >
                    <!-- Imagen del evento -->
                    <div class="h-48 bg-gradient-to-br from-[#B3224D] to-[#8d1a3c] flex items-center justify-center">
                        <component 
                            :is="evento.icono" 
                            :size="100" 
                            :stroke-width="1.5"
                            class="text-white/90"
                        />
                    </div>

                    <!-- Contenido -->
                    <div class="p-5">
                        <span class="inline-block px-3 py-1 bg-[#B3224D]/10 text-[#B3224D] rounded-full text-xs font-semibold mb-3">
                            {{ evento.categoria }}
                        </span>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2 line-clamp-2">
                            {{ evento.nombre }}
                        </h3>
                        <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                            <p class="flex items-center gap-2">
                                <Calendar :size="16" :stroke-width="2" class="text-[#B3224D]" />
                                {{ formatDate(evento.fecha) }}
                            </p>
                            <p class="flex items-center gap-2">
                                <MapPin :size="16" :stroke-width="2" class="text-[#B3224D]" />
                                {{ evento.lugar }}
                            </p>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-xl font-bold text-[#B3224D]">
                                {{ evento.precioMinimo }}
                            </span>
                            <RouterLink 
                                :to="`/eventos/${evento.id}`"
                                class="px-4 py-2 bg-[#B3224D] text-white rounded-lg hover:bg-[#8d1a3c] transition text-sm font-semibold"
                            >
                                Ver más
                            </RouterLink>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Ver todos -->
            <div class="text-center mt-12">
                <RouterLink to="/eventos">
                    <ButtonPrimary name="Ver Todos los Eventos" :flecha="true" />
                </RouterLink>
            </div>
        </div>
    </section>
</template>
