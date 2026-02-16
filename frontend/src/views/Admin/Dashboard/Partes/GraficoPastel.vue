<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import { PieChart } from 'lucide-vue-next';

Chart.register(...registerables);

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

const chartCanvas = ref(null);
let chartInstance = null;

const colores = [
    '#B3224D', '#8d1a3c', '#FF6384', '#36A2EB',
    '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
];

const crearGrafico = () => {
    if (!chartCanvas.value || props.loading) return;

    if (chartInstance) {
        chartInstance.destroy();
    }

    const ctx = chartCanvas.value.getContext('2d');

    const zonas = props.datos.map(d => d.zona);
    const ingresos = props.datos.map(d => d.ingresos);
    const coloresAsignados = colores.slice(0, zonas.length);

    chartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: zonas,
            datasets: [{
                label: 'Ingresos (S/)',
                data: ingresos,
                backgroundColor: coloresAsignados,
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: S/ ${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
};

watch(() => props.datos, () => {
    nextTick(() => {
        crearGrafico();
    });
}, { deep: true });

watch(() => props.loading, (newVal) => {
    if (!newVal) {
        nextTick(() => {
            crearGrafico();
        });
    }
});

onMounted(() => {
    if (!props.loading && props.datos.length > 0) {
        nextTick(() => {
            crearGrafico();
        });
    }
});
</script>

<template>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center gap-3 mb-6">
            <PieChart :size="24" :stroke-width="2" class="text-[#B3224D]" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Distribución de Ingresos por Zona
            </h3>
        </div>

        <div v-if="loading" class="animate-pulse">
            <div class="h-64 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto w-64"></div>
        </div>

        <div v-else-if="datos.length === 0"
            class="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
            <p>No hay datos disponibles</p>
        </div>

        <div v-else class="relative h-64">
            <canvas ref="chartCanvas"></canvas>
        </div>
    </div>
</template>
