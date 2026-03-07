<script setup>
import { computed } from 'vue';
import { MapPin, Ticket, DollarSign, Percent, Calendar, Clock } from 'lucide-vue-next';

const props = defineProps({
    datos: {
        type: Array,
        default: () => []
    },
    loading: {
        type: Boolean,
        default: false
    }
});

const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-PE', {
        style: 'currency',
        currency: 'PEN'
    }).format(value);
};

const formatFecha = (fecha) => {
    if (!fecha) return '';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-PE', { 
        day: '2-digit', 
        month: 'short',
        year: 'numeric'
    });
};

const formatHora = (hora) => {
    if (!hora) return '';
    return hora.substring(0, 5); // HH:MM
};

const porcentajeOcupacion = (zona) => {
    if (zona.capacidad === 0) return 0;
    return Math.round((zona.vendidos / zona.capacidad) * 100);
};

const getColorOcupacion = (porcentaje) => {
    if (porcentaje >= 90) return { text: 'text-red-600', bg: 'bg-red-100 dark:bg-red-900/30', bar: 'bg-red-500' };
    if (porcentaje >= 70) return { text: 'text-orange-600', bg: 'bg-orange-100 dark:bg-orange-900/30', bar: 'bg-orange-500' };
    if (porcentaje >= 40) return { text: 'text-blue-600', bg: 'bg-blue-100 dark:bg-blue-900/30', bar: 'bg-blue-500' };
    return { text: 'text-green-600', bg: 'bg-green-100 dark:bg-green-900/30', bar: 'bg-green-500' };
};
</script>

<template>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center gap-3 mb-6">
            <div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-full">
                <MapPin :size="24" :stroke-width="2" class="text-purple-600" />
            </div>
            <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                    Detalle por Zona y Presentación
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                    Ventas y recaudación por cada zona
                </p>
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="i in 3" :key="i" class="animate-pulse">
                <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-48"></div>
            </div>
        </div>

        <!-- Cards de Zonas -->
        <div v-else-if="datos.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="zona in datos" :key="zona.zona + zona.presentacion_fecha"
                class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-5 hover:shadow-lg transition-shadow">
                
                <!-- Header de Zona -->
                <div class="mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
                    <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
                        {{ zona.zona }}
                    </h4>
                    <div class="space-y-1">
                        <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <Calendar :size="14" :stroke-width="2" />
                            <span>{{ formatFecha(zona.presentacion_fecha) }}</span>
                        </div>
                        <div v-if="zona.presentacion_hora" class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <Clock :size="14" :stroke-width="2" />
                            <span>{{ formatHora(zona.presentacion_hora) }}</span>
                        </div>
                    </div>
                </div>

                <!-- Estadísticas -->
                <div class="space-y-4">
                    <!-- Tickets Vendidos -->
                    <div class="flex items-start justify-between gap-3">
                        <div class="flex items-center gap-2">
                            <div class="bg-blue-100 dark:bg-blue-900/30 p-2 rounded-lg">
                                <Ticket :size="18" :stroke-width="2" class="text-blue-600" />
                            </div>
                            <div>
                                <p class="text-xs text-gray-500 dark:text-gray-400">Tickets Vendidos</p>
                                <p class="text-lg font-bold text-gray-900 dark:text-white">
                                    {{ zona.vendidos }} <span class="text-sm font-normal text-gray-500">/ {{ zona.capacidad }}</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Total Recaudado -->
                    <div class="flex items-start justify-between gap-3">
                        <div class="flex items-center gap-2">
                            <div class="bg-green-100 dark:bg-green-900/30 p-2 rounded-lg">
                                <DollarSign :size="18" :stroke-width="2" class="text-green-600" />
                            </div>
                            <div>
                                <p class="text-xs text-gray-500 dark:text-gray-400">Recaudación</p>
                                <p class="text-lg font-bold text-green-600 dark:text-green-400">
                                    {{ formatCurrency(zona.ingresos) }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Porcentaje de Ocupación -->
                    <div class="pt-3 border-t border-gray-200 dark:border-gray-700">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center gap-2">
                                <Percent :size="16" :stroke-width="2" class="text-gray-600 dark:text-gray-400" />
                                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Ocupación
                                </span>
                            </div>
                            <span :class="[getColorOcupacion(porcentajeOcupacion(zona)).text, getColorOcupacion(porcentajeOcupacion(zona)).bg]"
                                class="text-sm font-bold px-3 py-1 rounded-full">
                                {{ porcentajeOcupacion(zona) }}%
                            </span>
                        </div>
                        <!-- Barra de progreso -->
                        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                            <div class="h-2.5 rounded-full transition-all duration-300"
                                :class="getColorOcupacion(porcentajeOcupacion(zona)).bar"
                                :style="{ width: `${porcentajeOcupacion(zona)}%` }">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8">
            <MapPin :size="48" :stroke-width="1.5" class="mx-auto mb-3 text-gray-400" />
            <p class="text-gray-600 dark:text-gray-400">
                No hay zonas configuradas para este evento
            </p>
        </div>
    </div>
</template>
