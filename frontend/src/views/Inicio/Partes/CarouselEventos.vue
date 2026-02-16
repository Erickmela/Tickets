<script setup>
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import { ChevronLeft, ChevronRight, Calendar, MapPin } from 'lucide-vue-next';
import { eventosService } from '@/services/eventosService';

const eventos = ref([]);
const loading = ref(true);
const currentIndex = ref(0);
const autoplayInterval = ref(null);

// Obtener eventos de la última semana
const getEventosSemana = async () => {
    try {
        const todosEventos = await eventosService.getEventosActivos();

        // Filtrar eventos de la última semana
        const ahora = new Date();
        const unaSemanaAtras = new Date(ahora.getTime() - 7 * 24 * 60 * 60 * 1000);

        eventos.value = todosEventos.filter(evento => {
            const fechaCreacion = new Date(evento.fecha_creacion);
            return fechaCreacion >= unaSemanaAtras && evento.imagen_principal;
        }).slice(0, 6); // Máximo 6 eventos

    } catch (error) {
        console.error('Error cargando eventos:', error);
        eventos.value = [];
    } finally {
        loading.value = false;
    }
};

// Navegar anterior
const prev = () => {
    if (currentIndex.value > 0) {
        currentIndex.value--;
    } else {
        currentIndex.value = eventos.value.length - 1;
    }
    resetAutoplay();
};

// Navegar siguiente
const next = () => {
    if (currentIndex.value < eventos.value.length - 1) {
        currentIndex.value++;
    } else {
        currentIndex.value = 0;
    }
    resetAutoplay();
};

// Ir a un slide específico
const goToSlide = (index) => {
    currentIndex.value = index;
    resetAutoplay();
};

// Autoplay
const startAutoplay = () => {
    autoplayInterval.value = setInterval(() => {
        next();
    }, 5000); // Cambiar cada 5 segundos
};

const stopAutoplay = () => {
    if (autoplayInterval.value) {
        clearInterval(autoplayInterval.value);
    }
};

const resetAutoplay = () => {
    stopAutoplay();
    startAutoplay();
};

// Formatear fecha
const formatearFecha = (fecha) => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
};

// Obtener imagen del evento
const getImagenUrl = (imagen) => {
    if (!imagen) return null;
    if (imagen.startsWith('http')) return imagen;
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${imagen}`;
};

onMounted(() => {
    getEventosSemana();
    startAutoplay();
});

// Limpiar interval al desmontar
import { onUnmounted } from 'vue';
onUnmounted(() => {
    stopAutoplay();
});
</script>

<template>
    <section class="py-12 bg-white dark:bg-gray-900">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="text-center mb-8">
                <div class="inline-block mb-2">
                    <span class="text-[#B3224D] font-bold text-sm uppercase tracking-wider">
                        Novedades
                    </span>
                </div>
                <h2 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
                    Eventos de la
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#B3224D] to-[#8d1a3c]">
                        semana
                    </span>
                </h2>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="relative h-96 bg-gray-200 dark:bg-gray-800 rounded-3xl animate-pulse"></div>

            <!-- No hay eventos -->
            <div v-else-if="eventos.length === 0" class="text-center py-16 bg-gray-50 dark:bg-gray-800 rounded-3xl">
                <p class="text-gray-600 dark:text-gray-400">No hay eventos nuevos esta semana</p>
            </div>

            <!-- Carousel -->
            <div v-else class="relative group" @mouseenter="stopAutoplay" @mouseleave="startAutoplay">
                <!-- Contenedor de slides -->
                <div class="relative h-96 md:h-[600px] rounded-3xl overflow-hidden shadow-2xl">
                    <TransitionGroup name="slide">
                        <div v-for="(evento, index) in eventos" v-show="index === currentIndex" :key="evento.id"
                            class="absolute inset-0">
                            <!-- Imagen de fondo -->
                            <div class="absolute inset-0">
                                <img :src="getImagenUrl(evento.imagen_principal)" :alt="evento.nombre"
                                    class="w-full h-full object-cover" />
                                <!-- Overlay gradiente -->
                                <div
                                    class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
                                </div>
                            </div>

                            <!-- Contenido -->
                            <div class="absolute bottom-0 left-0 right-0 p-8 md:p-12">
                                <div class="max-w-3xl">
                                    <!-- Badge de región -->
                                    <div class="mb-4">
                                        <span
                                            class="inline-flex items-center gap-2 px-4 py-2 bg-[#B3224D] text-white rounded-full text-sm font-semibold shadow-lg">
                                            <MapPin :size="16" :stroke-width="2" />
                                            {{ evento.region || 'Lima' }}
                                        </span>
                                    </div>

                                    <!-- Título -->
                                    <h3 class="text-3xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">
                                        {{ evento.nombre }}
                                    </h3>

                                    <!-- Info -->
                                    <div class="flex flex-wrap items-center gap-6 mb-6 text-white/90">
                                        <div class="flex items-center gap-2">
                                            <Calendar :size="20" :stroke-width="2" />
                                            <span class="text-lg">{{ formatearFecha(evento.fecha) }}</span>
                                        </div>
                                        <div v-if="evento.lugar" class="flex items-center gap-2">
                                            <MapPin :size="20" :stroke-width="2" />
                                            <span class="text-lg">{{ evento.lugar }}</span>
                                        </div>
                                    </div>

                                    <!-- Botón -->
                                    <RouterLink :to="`/eventos/${evento.id}`"
                                        class="inline-block px-8 py-4 bg-white text-[#B3224D] font-bold rounded-2xl hover:bg-gray-100 transition-all hover:scale-105 shadow-lg">
                                        Ver detalles →
                                    </RouterLink>
                                </div>
                            </div>
                        </div>
                    </TransitionGroup>
                </div>

                <!-- Botones de navegación -->
                <button @click="prev"
                    class="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 flex items-center justify-center bg-white/90 dark:bg-gray-800/90 text-gray-900 dark:text-white rounded-full shadow-lg hover:bg-white dark:hover:bg-gray-700 transition-all opacity-0 group-hover:opacity-100 hover:scale-110">
                    <ChevronLeft :size="24" :stroke-width="2" />
                </button>
                <button @click="next"
                    class="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 flex items-center justify-center bg-white/90 dark:bg-gray-800/90 text-gray-900 dark:text-white rounded-full shadow-lg hover:bg-white dark:hover:bg-gray-700 transition-all opacity-0 group-hover:opacity-100 hover:scale-110">
                    <ChevronRight :size="24" :stroke-width="2" />
                </button>

                <!-- Indicadores -->
                <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                    <button v-for="(evento, index) in eventos" :key="index" @click="goToSlide(index)"
                        class="transition-all" :class="[
                            index === currentIndex
                                ? 'w-8 bg-white'
                                : 'w-2 bg-white/50 hover:bg-white/75'
                        ]" style="height: 8px; border-radius: 4px;"></button>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
/* Transiciones del slide */
.slide-enter-active,
.slide-leave-active {
    transition: all 0.6s ease;
}

.slide-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.slide-leave-to {
    opacity: 0;
    transform: translateX(-100%);
}
</style>
