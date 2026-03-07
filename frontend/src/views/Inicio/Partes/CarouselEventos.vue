<script setup>
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import { ChevronLeft, ChevronRight, Calendar, MapPin, Tag, Ticket } from 'lucide-vue-next';
import { eventosService } from '@/services/eventosService';

const eventos = ref([]);
const loading = ref(true);
const currentIndex = ref(0);
const autoplayInterval = ref(null);
const progressWidth = ref(0);
const progressInterval = ref(null);

// Obtener eventos de la última semana
const getEventosSemana = async () => {
    try {
        const todosEventos = await eventosService.getEventosLanding();

        // Filtrar eventos que tengan imagen principal
        eventos.value = todosEventos.filter(evento => evento.imagen_principal).slice(0, 6); // Máximo 6 eventos

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

// Autoplay con barra de progreso
const startAutoplay = () => {
    progressWidth.value = 0;
    autoplayInterval.value = setInterval(() => {
        next();
    }, 5000);
    
    // Animar barra de progreso
    progressInterval.value = setInterval(() => {
        progressWidth.value += 2;
        if (progressWidth.value >= 100) {
            progressWidth.value = 0;
        }
    }, 100);
};

const stopAutoplay = () => {
    if (autoplayInterval.value) {
        clearInterval(autoplayInterval.value);
    }
    if (progressInterval.value) {
        clearInterval(progressInterval.value);
    }
};

const resetAutoplay = () => {
    stopAutoplay();
    startAutoplay();
};

// Navegación con teclado
const handleKeydown = (e) => {
    if (e.key === 'ArrowLeft') prev();
    if (e.key === 'ArrowRight') next();
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
    // Eliminar /api del final si existe, ya que media se sirve desde la raíz
    const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/api$/, '');
    return `${baseUrl}${imagen}`;
};

onMounted(() => {
    getEventosSemana();
    startAutoplay();
    window.addEventListener('keydown', handleKeydown);
});

// Limpiar interval al desmontar
import { onUnmounted } from 'vue';
onUnmounted(() => {
    stopAutoplay();
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
    <section class="bg-white dark:bg-gray-900">
        <div class="mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="mb-8">
                <h2 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">
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
                            <!-- Imagen de fondo con efecto Ken Burns -->
                            <div class="absolute inset-0">
                                <img :src="getImagenUrl(evento.imagen_principal)" :alt="evento.nombre"
                                    class="w-full h-full object-cover animate-ken-burns" />
                                <!-- Overlay gradiente mejorado -->
                                <div
                                    class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-black/20">
                                </div>
                            </div>

                            <!-- Contenido -->
                            <div class="absolute bottom-0 left-0 right-0 p-6 md:p-12">
                                <div class="max-w-3xl">
                                    <!-- Badges superiores -->
                                    <div class="flex flex-wrap items-center gap-3 mb-4">
                                        <span
                                            class="inline-flex items-center gap-2 px-4 py-2 bg-[#B3224D] text-white rounded-full text-xs md:text-sm font-semibold shadow-lg backdrop-blur-sm">
                                            <MapPin :size="16" :stroke-width="2" />
                                            {{ evento.region || 'Lima' }}
                                        </span>
                                        <span v-if="evento.categoria_nombre"
                                            class="inline-flex items-center gap-2 px-4 py-2 bg-white/20 text-white rounded-full text-xs md:text-sm font-semibold shadow-lg backdrop-blur-sm">
                                            <Tag :size="16" :stroke-width="2" />
                                            {{ evento.categoria_nombre }}
                                        </span>
                                    </div>

                                    <!-- Título -->
                                    <h3 class="text-2xl md:text-5xl font-bold text-white mb-3 md:mb-4 drop-shadow-2xl leading-tight">
                                        {{ evento.nombre }}
                                    </h3>

                                    <!-- Info -->
                                    <div class="flex flex-wrap items-center gap-4 md:gap-6 mb-4 md:mb-6 text-white">
                                        <div class="flex items-center gap-2">
                                            <Calendar :size="18" :stroke-width="2" class="flex-shrink-0" />
                                            <span class="text-sm md:text-lg font-medium">{{ formatearFecha(evento.fecha) }}</span>
                                        </div>
                                        <div v-if="evento.lugar" class="flex items-center gap-2">
                                            <MapPin :size="18" :stroke-width="2" class="flex-shrink-0" />
                                            <span class="text-sm md:text-lg font-medium line-clamp-1">{{ evento.lugar }}</span>
                                        </div>
                                    </div>

                                    <!-- Precio y botón -->
                                    <div class="flex flex-wrap items-center gap-4">
                                        <div v-if="evento.precio_desde" class="bg-white/20 backdrop-blur-sm px-4 md:px-6 py-3 rounded-2xl border-2 border-white/30">
                                            <div class="flex items-center gap-2">
                                                <div>
                                                    <p class="text-white/80 text-xs font-medium">Desde</p>
                                                    <p class="text-white text-xl md:text-2xl font-bold">S/ {{ evento.precio_desde.toFixed(2) }}</p>
                                                </div>
                                            </div>
                                        </div>
                                        <RouterLink :to="`/eventos/${evento.nombre}`"
                                            class="inline-flex items-center gap-2 px-6 md:px-8 py-3 md:py-4 bg-white text-[#B3224D] font-bold rounded-2xl hover:bg-gray-100 transition-all hover:scale-105 shadow-xl">
                                            <span>Ver detalles</span>
                                            <span class="text-xl">→</span>
                                        </RouterLink>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </TransitionGroup>
                </div>

                <!-- Botones de navegación -->
                <button @click="prev" aria-label="Anterior"
                    class="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 md:w-14 md:h-14 flex items-center justify-center bg-white/90 dark:bg-gray-800/90 text-gray-900 dark:text-white rounded-full shadow-xl hover:bg-white dark:hover:bg-gray-700 transition-all md:opacity-0 md:group-hover:opacity-100 hover:scale-110 backdrop-blur-sm">
                    <ChevronLeft :size="24" :stroke-width="2.5" />
                </button>
                <button @click="next" aria-label="Siguiente"
                    class="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 md:w-14 md:h-14 flex items-center justify-center bg-white/90 dark:bg-gray-800/90 text-gray-900 dark:text-white rounded-full shadow-xl hover:bg-white dark:hover:bg-gray-700 transition-all md:opacity-0 md:group-hover:opacity-100 hover:scale-110 backdrop-blur-sm">
                    <ChevronRight :size="24" :stroke-width="2.5" />
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

/* Efecto Ken Burns - zoom suave en imágenes */
@keyframes kenBurns {
    0% {
        transform: scale(1);
    }
    100% {
        transform: scale(1.1);
    }
}

.animate-ken-burns {
    animation: kenBurns 20s ease-in-out infinite alternate;
}

/* Limitar texto */
.line-clamp-1 {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>
