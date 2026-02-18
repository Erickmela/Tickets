<script setup>
import { computed } from 'vue';
import { BarChart3, Inbox } from 'lucide-vue-next';

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  tipo: {
    type: String,
    default: 'ventas'
  },
  loading: {
    type: Boolean,
    default: false
  }
});

// Títulos según el tipo de reporte
const tituloGrafico = computed(() => {
  const titulos = {
    ventas: 'Tendencia de Ventas',
    validaciones: 'Tendencia de Validaciones',
    eventos: 'Ocupación de Eventos',
    personal: 'Rendimiento del Personal'
  };
  return titulos[props.tipo] || 'Gráfico Estadístico';
});

// Obtener el valor máximo para escalar el gráfico
const valorMaximo = computed(() => {
  if (!props.data.length) return 100;
  const valores = props.data.map(item => item.ventas || item.validaciones || item.cantidad || 0);
  return Math.max(...valores, 10);
});

// Calcular la altura de cada barra en porcentaje
const calcularAltura = (valor) => {
  return (valor / valorMaximo.value) * 100;
};

// Formatear fecha
const formatearFecha = (fecha) => {
  const date = new Date(fecha);
  return date.toLocaleDateString('es-PE', { day: '2-digit', month: 'short' });
};

// Formatear moneda
const formatearMoneda = (monto) => {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN'
  }).format(monto);
};
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-2">
        <BarChart3 :size="20" :stroke-width="2" class="text-[#B3224D]" />
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white">
          {{ tituloGrafico }}
        </h3>
      </div>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Visualización de datos en el período seleccionado
      </p>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="animate-pulse">
      <div class="h-64 bg-gray-200 rounded mb-4"></div>
      <div class="flex justify-between">
        <div class="h-4 bg-gray-200 rounded w-16"></div>
        <div class="h-4 bg-gray-200 rounded w-16"></div>
        <div class="h-4 bg-gray-200 rounded w-16"></div>
        <div class="h-4 bg-gray-200 rounded w-16"></div>
      </div>
    </div>

    <!-- Sin Datos -->
    <div v-else-if="!data.length" class="text-center py-12">
      <Inbox :size="64" :stroke-width="1.5" class="mx-auto mb-4 text-gray-400" />
      <p class="text-gray-600 dark:text-gray-400 font-medium">No hay datos para mostrar en este período</p>
      <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">Intenta ajustar los filtros de búsqueda</p>
    </div>

    <!-- Gráfico de Barras -->
    <div v-else>
      <!-- Area del Gráfico -->
      <div class="relative h-64 mb-4">
        <!-- Líneas de guía horizontales -->
        <div class="absolute inset-0 flex flex-col justify-between">
          <div class="border-t border-gray-200"></div>
          <div class="border-t border-gray-200"></div>
          <div class="border-t border-gray-200"></div>
          <div class="border-t border-gray-200"></div>
          <div class="border-t border-gray-300"></div>
        </div>

        <!-- Barras -->
        <div class="absolute inset-0 flex items-end justify-around px-4">
          <div
            v-for="(item, index) in data"
            :key="index"
            class="flex flex-col items-center group flex-1 mx-1"
          >
            <!-- Tooltip -->
            <div class="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-full mb-2 bg-gray-800 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
              <div>Cantidad: {{ item.ventas || item.validaciones || item.cantidad }}</div>
              <div v-if="item.ingresos">{{ formatearMoneda(item.ingresos) }}</div>
            </div>

            <!-- Barra -->
            <div
              class="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-lg transition-all hover:from-blue-700 hover:to-blue-500 cursor-pointer"
              :style="{ height: `${calcularAltura(item.ventas || item.validaciones || item.cantidad)}%` }"
            >
              <!-- Valor sobre la barra -->
              <div class="text-xs font-semibold text-gray-700 -mt-6 text-center">
                {{ item.ventas || item.validaciones || item.cantidad }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Etiquetas del eje X -->
      <div class="flex justify-around px-4">
        <div
          v-for="(item, index) in data"
          :key="`label-${index}`"
          class="text-xs text-gray-600 text-center flex-1"
        >
          {{ formatearFecha(item.fecha) }}
        </div>
      </div>

      <!-- Leyenda -->
      <div class="mt-6 pt-4 border-t border-gray-200 flex items-center justify-center gap-6">
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-gradient-to-t from-blue-600 to-blue-400 rounded"></div>
          <span class="text-sm text-gray-700">
            {{ tipo === 'ventas' ? 'Ventas' : tipo === 'validaciones' ? 'Validaciones' : 'Cantidad' }}
          </span>
        </div>
        <div v-if="tipo === 'ventas'" class="flex items-center gap-2">
          <div class="w-4 h-4 bg-gradient-to-t from-green-600 to-green-400 rounded"></div>
          <span class="text-sm text-gray-700">Ingresos</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para el gráfico */
</style>
