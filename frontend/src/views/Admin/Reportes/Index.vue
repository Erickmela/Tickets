<script setup>
import { ref, onMounted, computed } from "vue";
import { useToasts } from "@/Helpers/useToasts";
import { useAuthStore } from "@/stores/auth";
import { useReportesStore } from "@/stores/reportes";
import reportesService from "@/services/reportesService";
import { BarChart3, FileText, FileSpreadsheet } from "lucide-vue-next";

import AdmLayout from "@/Layouts/AdmLayout.vue";
import HeaderSecction from "@/components/Admin/Header.vue";
import ToastNotification from "@/components/ToastNotification.vue";

// Importar componentes de reportes
import TarjetasResumen from "./Partes/TarjetasResumen.vue";
import GraficoVentas from "./Partes/GraficoVentas.vue";
import TablaReportes from "./Partes/TablaReportes.vue";
import FiltrosReportes from "./Partes/FiltrosReportes.vue";

const toast = ref(null);
const toastHelper = useToasts(toast);
const authStore = useAuthStore();
const reportesStore = useReportesStore();

// Estado de carga
const isLoading = ref(false);

// Filtros para reportes
const filtros = ref({
  fecha_inicio: null,
  fecha_fin: null,
  evento_id: null,
  tipo_reporte: 'ventas', // 'ventas', 'validaciones', 'eventos', 'personal'
});

// Datos de reportes
const reporteData = ref({
  resumen: {
    total_ventas: 0,
    total_tickets: 0,
    total_validados: 0,
    ingresos_totales: 0,
    tasa_validacion: 0,
  },
  grafico: [],
  detalles: [],
});

/**
 * Obtener datos de reportes según filtros
 */
const fetchReportes = async () => {
  isLoading.value = true;
  
  try {
    const params = {
      fecha_inicio: filtros.value.fecha_inicio,
      fecha_fin: filtros.value.fecha_fin,
      evento_id: filtros.value.evento_id,
    };

    let response;

    // Llamar al endpoint correspondiente según el tipo de reporte
    switch (filtros.value.tipo_reporte) {
      case 'ventas':
        response = await reportesService.getReporteVentas(params);
        break;
      case 'validaciones':
        response = await reportesService.getReporteValidaciones(params);
        break;
      case 'eventos':
        response = await reportesService.getReporteEventos(params);
        break;
      case 'personal':
        response = await reportesService.getReportePersonal(params);
        break;
      default:
        response = await reportesService.getReporteVentas(params);
    }

    // Asignar datos según el tipo de reporte
    if (filtros.value.tipo_reporte === 'ventas') {
      reporteData.value = {
        resumen: response.resumen,
        grafico: response.grafico,
        detalles: response.detalles,
      };
    } else {
      reporteData.value = {
        resumen: {
          total_ventas: response.total_validaciones || response.total_ventas || 0,
          total_tickets: response.total_validaciones || 0,
          total_validados: response.validaciones_exitosas || 0,
          ingresos_totales: 0,
          tasa_validacion: 0,
        },
        grafico: response.grafico || [],
        detalles: response.detalles || [],
      };
    }
    
    toastHelper.success('Reporte generado exitosamente');
  } catch (error) {
    console.error('Error al generar reporte:', error);
    toastHelper.error(error.response?.data?.error || 'Error al generar reporte');
    // Resetear datos en caso de error
    reporteData.value = {
      resumen: {
        total_ventas: 0,
        total_tickets: 0,
        total_validados: 0,
        ingresos_totales: 0,
        tasa_validacion: 0,
      },
      grafico: [],
      detalles: [],
    };
  } finally {
    isLoading.value = false;
  }
};

/**
 * Aplicar filtros y regenerar reporte
 */
const aplicarFiltros = (nuevosFiltros) => {
  filtros.value = { ...filtros.value, ...nuevosFiltros };
  fetchReportes();
};

/**
 * Exportar reporte a PDF/Excel
 */
const exportarReporte = async (formato) => {
  try {
    isLoading.value = true;
    toastHelper.info(`Generando archivo ${formato.toUpperCase()}...`);
    
    if (formato === 'pdf') {
      await reportesService.exportarPDF(filtros.value.tipo_reporte, {
        fecha_inicio: filtros.value.fecha_inicio,
        fecha_fin: filtros.value.fecha_fin,
        evento_id: filtros.value.evento_id,
      });
    } else if (formato === 'excel') {
      await reportesService.exportarExcel(filtros.value.tipo_reporte, {
        fecha_inicio: filtros.value.fecha_inicio,
        fecha_fin: filtros.value.fecha_fin,
        evento_id: filtros.value.evento_id,
      });
    }
    
    toastHelper.success(`Reporte exportado a ${formato.toUpperCase()} exitosamente`);
  } catch (error) {
    console.error('Error al exportar:', error);
    toastHelper.error(error.response?.data?.error || `Error al exportar a ${formato.toUpperCase()}`);
  } finally {
    isLoading.value = false;
  }
};

/**
 * Limpiar filtros
 */
const limpiarFiltros = () => {
  filtros.value = {
    fecha_inicio: null,
    fecha_fin: null,
    evento_id: null,
    tipo_reporte: 'ventas',
  };
  fetchReportes();
};

onMounted(() => {
  // Cargar datos iniciales
  fetchReportes();
});
</script>

<template>
  <AdmLayout>
    <ToastNotification ref="toast" />

    <HeaderSecction 
      title="Reportes y Estadísticas" 
      description="Análisis detallado de ventas, validaciones y eventos del sistema"
    >
      <template #icon>
        <BarChart3 :size="32" :stroke-width="2" class="text-[#B3224D]" />
      </template>
      <template #actions>
        <button
          @click="exportarReporte('pdf')"
          :disabled="isLoading"
          class="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <FileText :size="18" />
          <span>Exportar PDF</span>
        </button>
        <button
          @click="exportarReporte('excel')"
          :disabled="isLoading"
          class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <FileSpreadsheet :size="18" />
          <span>Exportar Excel</span>
        </button>
      </template>
    </HeaderSecction>

    <div class="space-y-6">
      <!-- Filtros de Reportes -->
      <FiltrosReportes
        :filtros="filtros"
        @aplicar="aplicarFiltros"
        @limpiar="limpiarFiltros"
      />

      <!-- Tarjetas de Resumen -->
      <TarjetasResumen
        :data="reporteData.resumen"
        :loading="isLoading"
      />

      <!-- Gráfico de Ventas/Estadísticas -->
      <GraficoVentas
        :data="reporteData.grafico"
        :tipo="filtros.tipo_reporte"
        :loading="isLoading"
      />

      <!-- Tabla de Detalles -->
      <TablaReportes
        :data="reporteData.detalles"
        :tipo="filtros.tipo_reporte"
        :loading="isLoading"
      />
    </div>
  </AdmLayout>
</template>

<style scoped>
/* Estilos personalizados si son necesarios */
</style>
