<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import { TrendingUp } from 'lucide-vue-next';

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

    if (chartInstance) {
        chartInstance.destroy();
    }

    const ctx = chartCanvas.value.getContext('2d');

    const fechas = props.datos.map(d => d.fecha);
    const ventas = props.datos.map(d => d.ventas);
    const ingresos = props.datos.map(d => d.ingresos);

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: fechas,
            datasets: [
                {
                    label: 'Número de Ventas',
                    data: ventas,
                    borderColor: '#B3224D',
                    backgroundColor: 'rgba(179, 34, 77, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Ingresos (S/)',
                    data: ingresos,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                if (context.datasetIndex === 1) {
                                    label += 'S/ ' + context.parsed.y.toFixed(2);
                                } else {
                                    label += context.parsed.y;
                                }
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Número de Ventas'
                    },
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Ingresos (S/)'
                    },
                    beginAtZero: true,
                    grid: {
                        drawOnChartArea: false,
                    },
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
            <TrendingUp :size="24" :stroke-width="2" class="text-[#B3224D]" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Evolución de Ventas e Ingresos
            </h3>
        </div>

        <div v-if="loading" class="animate-pulse">
            <div class="h-72 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>

        <div v-else-if="datos.length === 0"
            class="flex items-center justify-center h-72 text-gray-500 dark:text-gray-400">
            <p>No hay datos disponibles</p>
        </div>

        <div v-else class="relative h-72">
            <canvas ref="chartCanvas"></canvas>
        </div>
    </div>
</template>
