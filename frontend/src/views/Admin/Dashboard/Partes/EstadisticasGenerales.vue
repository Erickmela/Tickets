<script setup>
import { computed } from 'vue';
import { TrendingUp, Users, DollarSign, Ticket, Percent } from 'lucide-vue-next';

const props = defineProps({
    estadisticas: {
        type: Object,
        default: () => ({
            totalVentas: 0,
            totalIngresos: 0,
            ticketsVendidos: 0,
            ticketsDisponibles: 0,
            porcentajeOcupacion: 0
        })
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

const capacidadTotal = computed(() => {
    return props.estadisticas.ticketsVendidos + props.estadisticas.ticketsDisponibles;
});

const tarjetas = computed(() => [
    {
        icon: DollarSign,
        titulo: 'Ingresos Totales',
        valor: formatCurrency(props.estadisticas.totalIngresos),
        color: 'text-green-600',
        bg: 'bg-green-100 dark:bg-green-900/30'
    },
    {
        icon: TrendingUp,
        titulo: 'Ventas Realizadas',
        valor: props.estadisticas.totalVentas,
        color: 'text-blue-600',
        bg: 'bg-blue-100 dark:bg-blue-900/30'
    },
    {
        icon: Ticket,
        titulo: 'Tickets Vendidos',
        valor: `${props.estadisticas.ticketsVendidos} / ${capacidadTotal.value}`,
        color: 'text-purple-600',
        bg: 'bg-purple-100 dark:bg-purple-900/30'
    },
    {
        icon: Percent,
        titulo: 'Ocupación',
        valor: `${props.estadisticas.porcentajeOcupacion}%`,
        color: 'text-orange-600',
        bg: 'bg-orange-100 dark:bg-orange-900/30'
    }
]);
</script>

<template>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="(tarjeta, index) in tarjetas" :key="index"
            class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow">
            <div v-if="loading" class="animate-pulse">
                <div class="flex items-center justify-between mb-4">
                    <div class="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                </div>
                <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>

            <div v-else>
                <div class="flex items-center justify-between mb-4">
                    <div :class="[tarjeta.bg, 'p-3 rounded-full']">
                        <component :is="tarjeta.icon" :size="24" :stroke-width="2" :class="tarjeta.color" />
                    </div>
                </div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                    {{ tarjeta.titulo }}
                </p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">
                    {{ tarjeta.valor }}
                </p>
            </div>
        </div>
    </div>
</template>
