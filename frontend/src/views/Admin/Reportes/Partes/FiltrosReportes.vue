<script setup>
import { ref, watch, computed } from 'vue';
import { Search, X } from 'lucide-vue-next';

const props = defineProps({
  filtros: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['aplicar', 'limpiar']);

// Copia local de filtros
const filtrosLocal = ref({ ...props.filtros });

// Opciones de tipo de reporte
const tiposReporte = [
  { value: 'ventas', label: 'Ventas' },
  { value: 'validaciones', label: 'Validaciones' },
  { value: 'eventos', label: 'Eventos' },
  { value: 'personal', label: 'Personal' }
];

// Aplicar filtros
const aplicarFiltros = () => {
  emit('aplicar', filtrosLocal.value);
};

// Limpiar filtros
const limpiarFiltros = () => {
  filtrosLocal.value = {
    fecha_inicio: null,
    fecha_fin: null,
    evento_id: null,
    tipo_reporte: 'ventas',
  };
  emit('limpiar');
};

// Obtener fecha de hoy
const hoy = computed(() => {
  const fecha = new Date();
  return fecha.toISOString().split('T')[0];
});

// Fecha de hace 30 días
const hace30Dias = computed(() => {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() - 30);
  return fecha.toISOString().split('T')[0];
});

// Watch para sincronizar con props
watch(() => props.filtros, (newVal) => {
  filtrosLocal.value = { ...newVal };
}, { deep: true });
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <div class="flex items-center gap-2 mb-4">
      <Search :size="20" :stroke-width="2" class="text-[#B3224D]" />
      <h3 class="text-lg font-semibold text-gray-800 dark:text-white">
        Filtros de Búsqueda
      </h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Tipo de Reporte -->
      <div class="flex flex-col">
        <label class="text-sm font-medium text-gray-700 mb-2">
          Tipo de Reporte
        </label>
        <select
          v-model="filtrosLocal.tipo_reporte"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option v-for="tipo in tiposReporte" :key="tipo.value" :value="tipo.value">
            {{ tipo.label }}
          </option>
        </select>
      </div>

      <!-- Fecha Inicio -->
      <div class="flex flex-col">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Fecha Inicio
        </label>
        <input
          type="date"
          v-model="filtrosLocal.fecha_inicio"
          :max="hoy"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <!-- Fecha Fin -->
      <div class="flex flex-col">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Fecha Fin
        </label>
        <input
          type="date"
          v-model="filtrosLocal.fecha_fin"
          :max="hoy"
          :min="filtrosLocal.fecha_inicio"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <!-- Botones de Acción -->
      <div class="flex flex-col justify-end">
        <div class="flex gap-2">
          <button
            @click="aplicarFiltros"
            class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Search :size="16" />
            <span>Aplicar</span>
          </button>
          <button
            @click="limpiarFiltros"
            class="inline-flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            <X :size="16" />
            <span>Limpiar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Filtros Rápidos -->
    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Filtros rápidos:</p>
      <div class="flex gap-2 flex-wrap">
        <button
          @click="filtrosLocal.fecha_inicio = hoy; filtrosLocal.fecha_fin = hoy; aplicarFiltros()"
          class="px-3 py-1 text-sm bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
        >
          Hoy
        </button>
        <button
          @click="filtrosLocal.fecha_inicio = hace30Dias; filtrosLocal.fecha_fin = hoy; aplicarFiltros()"
          class="px-3 py-1 text-sm bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
        >
          Últimos 30 días
        </button>
        <button
          @click="filtrosLocal.fecha_inicio = null; filtrosLocal.fecha_fin = null; aplicarFiltros()"
          class="px-3 py-1 text-sm bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
        >
          Todo el tiempo
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos personalizados */
input[type="date"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
}
</style>
