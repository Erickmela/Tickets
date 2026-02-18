<script setup>
import { computed } from 'vue';
import { ShoppingCart, Ticket, CheckCircle, TrendingUp } from 'lucide-vue-next';

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      total_ventas: 0,
      total_tickets: 0,
      total_validados: 0,
      ingresos_totales: 0,
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const tarjetas = computed(() => [
  {
    titulo: 'Total Ventas',
    valor: props.data.total_ventas,
    icono: ShoppingCart,
    color: 'bg-blue-500',
    textColor: 'text-blue-600',
    descripcion: 'Ventas realizadas'
  },
  {
    titulo: 'Tickets Vendidos',
    valor: props.data.total_tickets,
    icono: Ticket,
    color: 'bg-purple-500',
    textColor: 'text-purple-600',
    descripcion: 'Total de tickets'
  },
  {
    titulo: 'Tickets Validados',
    valor: props.data.total_validados,
    icono: CheckCircle,
    color: 'bg-green-500',
    textColor: 'text-green-600',
    descripcion: 'Ya ingresaron al evento'
  },
  {
    titulo: 'Ingresos Totales',
    valor: `S/ ${Number(props.data.ingresos_totales || 0).toFixed(2)}`,
    icono: TrendingUp,
    color: 'bg-amber-500',
    textColor: 'text-amber-600',
    descripcion: 'Suma total de ingresos'
  }
]);

const porcentajeValidacion = computed(() => {
  if (props.data.total_tickets === 0) return 0;
  return (Number(props.data.total_validados || 0) / Number(props.data.total_tickets || 1) * 100).toFixed(1);
});
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <div
      v-for="(tarjeta, index) in tarjetas"
      :key="index"
      class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
    >
      <!-- Skeleton Loading -->
      <div v-if="loading" class="animate-pulse">
        <div class="h-12 bg-gray-200 dark:bg-gray-700 rounded mb-3"></div>
        <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
      </div>

      <!-- Contenido Real -->
      <div v-else>
        <div class="flex items-center justify-between mb-4">
          <div :class="[tarjeta.color, 'w-14 h-14 rounded-lg flex items-center justify-center']">
            <component :is="tarjeta.icono" :size="28" :stroke-width="2" class="text-white" />
          </div>
        </div>
        
        <h3 class="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">
          {{ tarjeta.titulo }}
        </h3>
        
        <p class="text-2xl font-bold text-gray-800 dark:text-white mb-2">
          {{ tarjeta.valor }}
        </p>
        
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {{ tarjeta.descripcion }}
        </p>

        <!-- Indicador de validación solo para la tarjeta de validados -->
        <div v-if="index === 2" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-600 dark:text-gray-400">Tasa de asistencia</span>
            <span class="font-semibold text-green-600 dark:text-green-400">{{ porcentajeValidacion }}%</span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-1">
            <div
              class="bg-green-500 dark:bg-green-600 h-2 rounded-full transition-all"
              :style="{ width: `${porcentajeValidacion}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Animación suave para las tarjetas */
.hover\:shadow-lg {
  transition: box-shadow 0.3s ease;
}
</style>
