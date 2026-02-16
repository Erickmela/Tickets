<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import ButtonPrimary from '@/components/Buttons/ButtonPrimary.vue';

const eventosDestacados = ref([]);
const loading = ref(true);

onMounted(async () => {
    // Aquí podrías cargar los eventos desde tu API
    // Por ahora mostramos datos de ejemplo
    setTimeout(() => {
        eventosDestacados.value = [
            {
                id: 1,
                nombre: 'Festival de Rock 2026',
                fecha: '2026-03-15',
                lugar: 'Estadio Nacional',
                precio: 'S/ 80.00',
                imagen: '🎸',
                categoria: 'Música'
            },
            {
                id: 2,
                nombre: 'Concierto de Cumbia',
                fecha: '2026-03-20',
                lugar: 'Arena Lima',
                precio: 'S/ 50.00',
                imagen: '🎵',
                categoria: 'Música'
            },
            {
                id: 3,
                nombre: 'Partido Universitario vs Alianza',
                fecha: '2026-03-25',
                lugar: 'Estadio Monumental',
                precio: 'S/ 60.00',
                imagen: '⚽',
                categoria: 'Deportes'
            },
            {
                id: 4,
                nombre: 'Obra: Romeo y Julieta',
                fecha: '2026-04-01',
                lugar: 'Teatro Municipal',
                precio: 'S/ 70.00',
                imagen: '🎭',
                categoria: 'Teatro'
            }
        ];
        loading.value = false;
    }, 500);
});

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
                        <span class="text-8xl">{{ evento.imagen }}</span>
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
                                <span>📅</span>
                                {{ formatDate(evento.fecha) }}
                            </p>
                            <p class="flex items-center gap-2">
                                <span>📍</span>
                                {{ evento.lugar }}
                            </p>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-xl font-bold text-[#B3224D]">
                                {{ evento.precio }}
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
