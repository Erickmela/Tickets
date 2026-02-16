<script setup>
import { ref, computed } from 'vue';
import AdmLayout from '@/Layouts/AdmLayout.vue';
import HeaderSecction from '@/components/Admin/Header.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import FiltroEvento from './Partes/FiltroEvento.vue';
import EstadisticasGenerales from './Partes/EstadisticasGenerales.vue';
import GraficoBarra from './Partes/GraficoBarra.vue';
import GraficoPastel from './Partes/GraficoPastel.vue';
import GraficoLinea from './Partes/GraficoLinea.vue';
import GenerarReporte from './Partes/GenerarReporte.vue';
import { useToasts } from '@/Helpers/useToasts';
import { eventosService } from '@/services/eventosService';
import { BarChart3 } from 'lucide-vue-next';

const toast = ref(null);
const toastHelper = useToasts(toast);

const eventoSeleccionado = ref(null);
const loading = ref(false);

const estadisticas = ref({
    totalVentas: 0,
    totalIngresos: 0,
    ticketsVendidos: 0,
    ticketsDisponibles: 0,
    porcentajeOcupacion: 0
});

const datosZonas = ref([]);
const datosIngresos = ref([]);
const datosEvolucion = ref([]);

const cargarDatosEvento = async (evento) => {
    try {
        loading.value = true;
        eventoSeleccionado.value = evento;

        // Obtener estadísticas completas desde el backend (optimizado)
        const stats = await eventosService.getEstadisticasEvento(evento.id);

        // Validar que el evento tenga zonas
        if (!stats.zonas || stats.zonas.length === 0) {
            toastHelper.warning('Este evento no tiene zonas configuradas');
            resetDatos();
            loading.value = false;
            return;
        }

        // Asignar estadísticas generales
        estadisticas.value = {
            totalVentas: stats.ventas.total_ventas,
            totalIngresos: stats.ventas.ingresos_totales,
            ticketsVendidos: stats.capacidad.vendidos,
            ticketsDisponibles: stats.capacidad.disponibles,
            porcentajeOcupacion: stats.capacidad.porcentaje_ocupacion
        };

        // Preparar datos para gráfico de barras (ventas por zona)
        datosZonas.value = stats.zonas.map(z => ({
            zona: z.nombre,
            vendidos: z.tickets_vendidos,
            disponibles: z.tickets_disponibles,
            capacidad: z.capacidad_maxima
        }));

        // Preparar datos para gráfico de pastel (ingresos por zona)
        datosIngresos.value = stats.zonas.map(z => ({
            zona: z.nombre,
            ingresos: z.ingresos,
            precio: z.precio
        }));

        // Obtener evolución de ventas (últimos 7 días)
        const evolucion = await eventosService.getEvolucionVentas(evento.id, 7);
        datosEvolucion.value = evolucion.map(e => ({
            fecha: e.fecha,
            ventas: e.ventas,
            ingresos: e.ingresos
        }));

    } catch (error) {
        console.error('Error al cargar datos del evento:', error);
        toastHelper.error('Error al cargar los datos del evento');
        resetDatos();
    } finally {
        loading.value = false;
    }
};

const resetDatos = () => {
    estadisticas.value = {
        totalVentas: 0,
        totalIngresos: 0,
        ticketsVendidos: 0,
        ticketsDisponibles: 0,
        porcentajeOcupacion: 0
    };
    datosZonas.value = [];
    datosIngresos.value = [];
    datosEvolucion.value = [];
};

const datosReporte = computed(() => ({
    totalVentas: estadisticas.value.totalVentas,
    totalIngresos: estadisticas.value.totalIngresos,
    ticketsVendidos: estadisticas.value.ticketsVendidos,
    ticketsDisponibles: estadisticas.value.ticketsDisponibles,
    porcentajeOcupacion: estadisticas.value.porcentajeOcupacion,
    zonas: datosZonas.value.map((zona, index) => ({
        zona: zona.zona,
        precio: datosIngresos.value[index]?.precio || 0,
        capacidad: zona.capacidad,
        vendidos: zona.vendidos,
        disponibles: zona.disponibles,
        ingresos: datosIngresos.value[index]?.ingresos || 0,
        ocupacion: zona.capacidad > 0
            ? Math.round((zona.vendidos / zona.capacidad) * 100)
            : 0
    }))
}));

const mostrarContenido = computed(() => eventoSeleccionado.value !== null);
</script>

<template>
    <AdmLayout>
        <ToastNotification ref="toast" />

        <HeaderSecction title="Dashboard de Ventas" description="Análisis y estadísticas de ventas por evento">
            <template #icon>
                <BarChart3 :size="32" :stroke-width="2" class="text-[#B3224D]" />
            </template>
        </HeaderSecction>

        <div class="space-y-6">
            <!-- Filtro de Evento -->
            <div class="flex justify-between items-start gap-4">
                <div class="flex-1">
                    <FiltroEvento @eventoSeleccionado="cargarDatosEvento" />
                </div>
                <GenerarReporte v-if="eventoSeleccionado" :evento="eventoSeleccionado" :datosReporte="datosReporte" />
            </div>

            <!-- Mensaje cuando no hay evento seleccionado -->
            <div v-if="!mostrarContenido && !loading"
                class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-8 text-center">
                <BarChart3 :size="64" :stroke-width="1.5" class="mx-auto mb-4 text-blue-600 dark:text-blue-400" />
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    Selecciona un evento para ver las estadísticas
                </h3>
                <p class="text-gray-600 dark:text-gray-400">
                    Elige un evento del selector arriba para visualizar los gráficos y reportes de ventas
                </p>
            </div>

            <!-- Contenido del Dashboard -->
            <template v-if="mostrarContenido">
                <!-- Estadísticas Generales -->
                <EstadisticasGenerales :estadisticas="estadisticas" :loading="loading" />

                <!-- Gráficos en Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Gráfico de Barras -->
                    <GraficoBarra :datos="datosZonas" :loading="loading" />

                    <!-- Gráfico de Pastel -->
                    <GraficoPastel :datos="datosIngresos" :loading="loading" />
                </div>

                <!-- Gráfico de Línea (ancho completo) -->
                <GraficoLinea :datos="datosEvolucion" :loading="loading" />
            </template>
        </div>
    </AdmLayout>
</template>
