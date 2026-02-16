<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import { BarChart3 } from 'lucide-vue-next';

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

const crearGrafico = () => {
    if (!chartCanvas.value || props.loading) return;

    // Destruir gráfico anterior si existe
    if (chartInstance) {
        chartInstance.destroy();
    }

    const ctx = chartCanvas.value.getContext('2d');

    const zonas = props.datos.map(d => d.zona);
    const vendidos = props.datos.map(d => d.vendidos);
    const disponibles = props.datos.map(d => d.disponibles);

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: zonas,
            datasets: [
                {
                    label: 'Vendidos',
                    data: vendidos,
                    backgroundColor: '#B3224D',
                    borderColor: '#8d1a3c',
                    borderWidth: 1
                },
                {
                    label: 'Disponibles',
                    data: disponibles,
                    backgroundColor: '#e5e7eb',
                    borderColor: '#9ca3af',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
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
            <BarChart3 :size="24" :stroke-width="2" class="text-[#B3224D]" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Ventas por Zona
            </h3>
        </div>

        <div v-if="loading" class="animate-pulse">
            <div class="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
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
