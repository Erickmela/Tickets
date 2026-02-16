<script setup>
import { RouterLink } from 'vue-router';
import { computed } from 'vue';
import { Calendar, MapPin, Tag, Music, Trophy, Drama, Mic, Tent, Utensils, PartyPopper, Sparkles } from 'lucide-vue-next';

const props = defineProps({
    evento: {
        type: Object,
        required: true
    }
});

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

// Obtener el icono de la categoría
const iconoCategoria = computed(() => {
    return categoriaIconos[props.evento.categoria] || Sparkles;
});

// Obtener la imagen principal o usar un fallback
const imagenEvento = computed(() => {
    if (props.evento.imagen_principal) {
        // Si la URL ya es completa, usarla directamente
        if (props.evento.imagen_principal.startsWith('http')) {
            return props.evento.imagen_principal;
        }
        // Si es una ruta relativa, agregar el prefijo del backend
        return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${props.evento.imagen_principal}`;
    }
    return null;
});

// Formatear fecha
const fechaFormateada = computed(() => {
    if (!props.evento.fecha) return '';
    const fecha = new Date(props.evento.fecha);
    return fecha.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
});

// Obtener precio mínimo
const precioMinimo = computed(() => {
    if (props.evento.zonas && props.evento.zonas.length > 0) {
        const precioMin = Math.min(...props.evento.zonas.map(z => parseFloat(z.precio)));
        return `S/ ${precioMin.toFixed(2)}`;
    }
    return 'Consultar';
});
</script>

<template>
    <RouterLink :to="`/eventos/${evento.id}`"
        class="group block bg-white dark:bg-gray-900 rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 overflow-hidden">
        <!-- Imagen del evento -->
        <div class="relative h-64 overflow-hidden bg-gradient-to-br from-[#B3224D]/20 to-purple-500/20">
            <!-- Si tiene imagen, mostrarla -->
            <img v-if="imagenEvento" :src="imagenEvento" :alt="evento.nombre"
                class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
            <!-- Si no tiene imagen, mostrar icono -->
            <div v-else
                class="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#B3224D] to-[#8d1a3c]">
                <component :is="iconoCategoria" :size="120" :stroke-width="1.5" class="text-white/90" />
            </div>

            <!-- Badge de estado -->
            <div class="absolute top-4 right-4">
                <span v-if="evento.estado === '2'"
                    class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-500 text-white shadow-lg">
                    <span class="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
                    Activo
                </span>
                <span v-else-if="evento.estado === '1'"
                    class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-[#B3224D] text-white shadow-lg">
                    Próximo
                </span>
            </div>

            <!-- Badge de categoría -->
            <div class="absolute top-4 left-4">
                <span
                    class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm text-gray-900 dark:text-white shadow-lg">
                    <component :is="iconoCategoria" :size="14" :stroke-width="2" />
                    {{ evento.categoria || 'Evento' }}
                </span>
            </div>
        </div>

        <!-- Contenido del evento -->
        <div class="p-6">
            <!-- Título -->
            <h3
                class="text-xl font-bold text-gray-900 dark:text-white mb-3 line-clamp-2 group-hover:text-[#B3224D] transition-colors">
                {{ evento.nombre }}
            </h3>

            <!-- Información -->
            <div class="space-y-2 mb-4">
                <!-- Fecha -->
                <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Calendar :size="18" :stroke-width="2" class="text-[#B3224D]" />
                    <span>{{ fechaFormateada }}</span>
                </div>

                <!-- Lugar -->
                <div v-if="evento.lugar" class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <MapPin :size="18" :stroke-width="2" class="text-[#B3224D]" />
                    <span class="line-clamp-1">{{ evento.lugar }}</span>
                </div>
            </div>

            <!-- Footer con precio y botón -->
            <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                <div>
                    <p class="text-xs text-gray-500 dark:text-gray-400">Desde</p>
                    <p class="text-2xl font-bold text-[#B3224D]">{{ precioMinimo }}</p>
                </div>
                <button
                    class="px-5 py-2.5 bg-[#B3224D] text-white rounded-xl font-semibold hover:bg-[#8d1a3c] transition-colors shadow-md hover:shadow-lg group-hover:scale-105 transform duration-200">
                    Ver más →
                </button>
            </div>
        </div>
    </RouterLink>
</template>
