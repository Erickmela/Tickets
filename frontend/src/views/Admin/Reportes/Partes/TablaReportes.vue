<script setup>
import { computed } from 'vue';
import { FileText, Inbox } from 'lucide-vue-next';

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

// Configuración de columnas según el tipo de reporte
const columnas = computed(() => {
  const configs = {
    ventas: [
      { key: 'id', label: 'ID', width: 'w-20' },
      { key: 'fecha', label: 'Fecha', width: 'w-32' },
      { key: 'evento', label: 'Evento', width: 'w-48' },
      { key: 'vendedor', label: 'Vendedor', width: 'w-32' },
      { key: 'tickets', label: 'Tickets', width: 'w-24', align: 'center' },
      { key: 'total', label: 'Total', width: 'w-28', align: 'right' },
    ],
    validaciones: [
      { key: 'id', label: 'ID', width: 'w-20' },
      { key: 'fecha', label: 'Fecha', width: 'w-40' },
      { key: 'ticket', label: 'Ticket', width: 'w-32' },
      { key: 'evento', label: 'Evento', width: 'w-48' },
      { key: 'validador', label: 'Validador', width: 'w-32' },
      { key: 'estado', label: 'Estado', width: 'w-24', align: 'center' },
    ],
    eventos: [
      { key: 'id', label: 'ID', width: 'w-20' },
      { key: 'nombre', label: 'Evento', width: 'w-64' },
      { key: 'fecha', label: 'Fecha', width: 'w-32' },
      { key: 'vendidos', label: 'Vendidos', width: 'w-24', align: 'center' },
      { key: 'disponibles', label: 'Disponibles', width: 'w-24', align: 'center' },
      { key: 'ocupacion', label: 'Ocupación', width: 'w-28', align: 'center' },
    ],
    personal: [
      { key: 'id', label: 'ID', width: 'w-20' },
      { key: 'nombre', label: 'Nombre', width: 'w-48' },
      { key: 'rol', label: 'Rol', width: 'w-32' },
      { key: 'ventas', label: 'Ventas', width: 'w-24', align: 'center' },
      { key: 'total', label: 'Total', width: 'w-32', align: 'right' },
    ],
  };
  return configs[props.tipo] || configs.ventas;
});

// Título de la tabla según el tipo
const tituloTabla = computed(() => {
  const titulos = {
    ventas: 'Detalle de Ventas',
    validaciones: 'Detalle de Validaciones',
    eventos: 'Detalle de Eventos',
    personal: 'Rendimiento del Personal'
  };
  return titulos[props.tipo] || 'Detalle del Reporte';
});

// Formatear fecha
const formatearFecha = (fecha) => {
  if (!fecha) return '-';
  const date = new Date(fecha);
  return date.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Formatear moneda
const formatearMoneda = (monto) => {
  if (!monto && monto !== 0) return '-';
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN'
  }).format(monto);
};

// Obtener alineación de texto
const getAlign = (align) => {
  const aligns = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right'
  };
  return aligns[align] || 'text-left';
};
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <div class="mb-4">
      <div class="flex items-center gap-2">
        <FileText :size="20" :stroke-width="2" class="text-[#B3224D]" />
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white">
          {{ tituloTabla }}
        </h3>
      </div>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="animate-pulse">
      <div class="h-12 bg-gray-200 rounded mb-2"></div>
      <div class="h-12 bg-gray-100 rounded mb-2"></div>
      <div class="h-12 bg-gray-200 rounded mb-2"></div>
      <div class="h-12 bg-gray-100 rounded mb-2"></div>
      <div class="h-12 bg-gray-200 rounded"></div>
    </div>

    <!-- Sin Datos -->
    <div v-else-if="!data.length" class="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg">
      <Inbox :size="64" :stroke-width="1.5" class="mx-auto mb-4 text-gray-400" />
      <p class="text-gray-600 dark:text-gray-400 font-medium">No hay registros detallados</p>
      <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">
        Los detalles aparecerán cuando haya datos en el período seleccionado
      </p>
    </div>

    <!-- Tabla de Datos -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <!-- Header -->
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th
              v-for="col in columnas"
              :key="col.key"
              :class="[col.width, getAlign(col.align), 'px-4 py-3 text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider']"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="(row, index) in data"
            :key="index"
            class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <td
              v-for="col in columnas"
              :key="`${index}-${col.key}`"
              :class="[getAlign(col.align), 'px-4 py-3 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap']"
            >
              <!-- Formateo especial según el tipo de columna -->
              <span v-if="col.key === 'fecha'">
                {{ formatearFecha(row[col.key]) }}
              </span>
              <span v-else-if="col.key === 'total' || col.key.includes('monto')">
                {{ formatearMoneda(row[col.key]) }}
              </span>
              <span v-else-if="col.key === 'ocupacion'">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': row[col.key] >= 80,
                    'bg-yellow-100 text-yellow-800': row[col.key] >= 50 && row[col.key] < 80,
                    'bg-red-100 text-red-800': row[col.key] < 50
                  }"
                >
                  {{ row[col.key] }}%
                </span>
              </span>
              <span v-else-if="col.key === 'estado'">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': row[col.key] === 'validado',
                    'bg-red-100 text-red-800': row[col.key] === 'rechazado',
                    'bg-yellow-100 text-yellow-800': row[col.key] === 'pendiente'
                  }"
                >
                  {{ row[col.key] }}
                </span>
              </span>
              <span v-else>
                {{ row[col.key] || '-' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Footer con resumen -->
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
        Mostrando {{ data.length }} {{ data.length === 1 ? 'registro' : 'registros' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para la tabla */
table {
  border-collapse: separate;
  border-spacing: 0;
}
</style>
