<script setup>
import { RouterLink } from 'vue-router';
import { computed } from 'vue';

const props = defineProps({
    evento: {
        type: Object,
        required: true
    }
});

// Obtener la imagen principal o usar un fallback
const imagenEvento = computed(() => {
    if (props.evento.imagen_principal) {
        // Si la URL ya es completa, usarla directamente
        if (props.evento.imagen_principal.startsWith('http')) {
            return props.evento.imagen_principal;
        }

        const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/api$/, '');
        return `${baseUrl}${props.evento.imagen_principal}`;
    }
    return null;
});

// Formatear fecha con día de la semana y hora en formato 12h
const fechaFormateada = computed(() => {
    if (!props.evento.fecha) return '';
    const fecha = new Date(props.evento.fecha);
    const diaSemana = fecha.toLocaleDateString('es-ES', { weekday: 'long' });
    const dia = fecha.getDate();
    const mes = fecha.toLocaleDateString('es-ES', { month: 'long' });
    
    // Formatear hora en formato 12h (am/pm)
    let horas = fecha.getHours();
    const minutos = fecha.getMinutes().toString().padStart(2, '0');
    const ampm = horas >= 12 ? 'pm' : 'am';
    horas = horas % 12 || 12; // Convertir a formato 12h
    
    return `${diaSemana.charAt(0).toUpperCase() + diaSemana.slice(1)} ${dia} de ${mes} - ${horas}:${minutos}${ampm}`;
});
</script>

<template>
    <!-- Card minimalista -->
    <RouterLink
        :to="`/eventos/${evento.slug}`"
        class="group flex flex-col bg-white dark:bg-gray-900 rounded-xl ">
        
        <!-- Imagen del evento - Ocupa la mayor parte del espacio -->
        <div class="relative h-60 overflow-hidden bg-gradient-to-br from-[#B3224D]/20 to-purple-500/20">
            <!-- Si tiene imagen, mostrarla -->
            <img v-if="imagenEvento" :src="imagenEvento" :alt="evento.nombre"
                class="w-full h-full object-fill group-hover:scale-105 transition-transform duration-500" />
            <!-- Si no tiene imagen, mostrar fondo de color -->
            <div v-else
                class="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#B3224D] to-[#8d1a3c]">
                <span class="text-white text-4xl font-bold opacity-20">{{ evento.nombre.charAt(0) }}</span>
            </div>
        </div>

        <!-- Contenido del evento - Simple y limpio -->
        <div class="mt-4 bg-white dark:bg-gray-900">
            <!-- Título -->
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2 line-clamp-2 group-hover:text-[#B3224D] transition-colors">
                {{ evento.nombre }}
            </h3>

            <!-- Fecha con hora -->
            <p class="text-lg text-gray-600 dark:text-gray-400">
                {{ fechaFormateada }}
            </p>
        </div>
    </RouterLink>
</template>

<style scoped>
.line-clamp-1 {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>
