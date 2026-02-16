<script setup>
import { ref } from 'vue';
import * as XLSX from 'xlsx';
import { FileDown, FileSpreadsheet, FileImage } from 'lucide-vue-next';
import ToastNotification from '@/components/ToastNotification.vue';
import { eventosService } from '@/services/eventosService';
import { useToasts } from '@/Helpers/useToasts';

const props = defineProps({
    evento: {
        type: Object,
        required: true
    },
    datosReporte: {
        type: Object,
        required: true
    }
});

const mostrarOpciones = ref(false);
const generandoReporte = ref(false);
const toast = ref(null);
const toastHelper = useToasts(toast);

const generarExcel = async () => {
    try {
        generandoReporte.value = true;

        // Obtener todos los tickets del evento
        const response = await eventosService.getTicketsReporte(props.evento.id);
        const { evento, tickets } = response;

        if (!tickets || tickets.length === 0) {
            toastHelper.warning('Este evento no tiene tickets vendidos');
            generandoReporte.value = false;
            return;
        }

        // Crear libro de trabajo
        const wb = XLSX.utils.book_new();

        // Hoja: Tickets del evento
        const ticketsData = [
            ['REPORTE DE TICKETS - ' + evento.nombre],
            [],
            ['Evento:', evento.nombre],
            ['Fecha:', evento.fecha],
            ['Hora:', evento.hora_inicio],
            ['Lugar:', evento.lugar],
            ['Región:', evento.region],
            [],
            [],
            ['UUID (Código Visual)', 'Token QR (Para Código QR)', 'Nombre Titular', 'DNI Titular', 'Zona', 'Precio', 'Estado', 'Fecha Compra']
        ];

        // Agregar cada ticket como una fila
        tickets.forEach(ticket => {
            ticketsData.push([
                ticket.codigo_uuid,           // UUID legible en el ticket impreso
                ticket.token_qr,              // Token encriptado para el QR Code
                ticket.nombre_titular,
                ticket.dni_titular,
                ticket.zona,
                'S/ ' + ticket.precio.toFixed(2),
                ticket.estado,
                ticket.fecha_compra
            ]);
        });

        // Crear hoja y agregarla al libro
        const ws = XLSX.utils.aoa_to_sheet(ticketsData);

        // Ajustar anchos de columna
        ws['!cols'] = [
            { wch: 38 }, // UUID
            { wch: 80 }, // Token QR (largo, encriptado)
            { wch: 30 }, // Nombre Titular
            { wch: 12 }, // DNI
            { wch: 20 }, // Zona
            { wch: 12 }, // Precio
            { wch: 10 }, // Estado
            { wch: 18 }  // Fecha Compra
        ];

        XLSX.utils.book_append_sheet(wb, ws, 'Tickets');

        // Generar y descargar archivo
        const nombreArchivo = `tickets_${props.evento.nombre.replace(/\s+/g, '_')}_${new Date().getTime()}.xlsx`;
        XLSX.writeFile(wb, nombreArchivo);

        toastHelper.success(`Reporte generado: ${tickets.length} tickets`);
        mostrarOpciones.value = false;
    } catch (error) {
        console.error('Error al generar Excel:', error);
        toastHelper.error('Error al generar el reporte Excel');
    } finally {
        generandoReporte.value = false;
    }
};

const generarCSV = async () => {
    try {
        generandoReporte.value = true;

        // Obtener todos los tickets del evento
        const response = await eventosService.getTicketsReporte(props.evento.id);
        const { evento, tickets } = response;

        if (!tickets || tickets.length === 0) {
            toastHelper.warning('Este evento no tiene tickets vendidos');
            generandoReporte.value = false;
            return;
        }

        // Crear contenido CSV
        let csv = 'REPORTE DE TICKETS - ' + evento.nombre + '\n\n';
        csv += 'Evento,' + evento.nombre + '\n';
        csv += 'Fecha,' + evento.fecha + '\n';
        csv += 'Hora,' + evento.hora_inicio + '\n';
        csv += 'Lugar,' + evento.lugar + '\n';
        csv += 'Región,' + evento.region + '\n\n';
        // Encabezados de columnas
        csv += 'UUID,Token QR (Para Código QR),Nombre Titular,DNI Titular,Zona,Precio,Estado,Fecha Compra\n';

        // Agregar cada ticket
        tickets.forEach(ticket => {
            csv += `${ticket.codigo_uuid},${ticket.token_qr},${ticket.nombre_titular},${ticket.dni_titular},${ticket.zona},S/ ${ticket.precio.toFixed(2)},${ticket.estado},${ticket.fecha_compra}\n`;
        });

        // Crear blob y descargar
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `tickets_${props.evento.nombre.replace(/\s+/g, '_')}_${new Date().getTime()}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        toastHelper.success(`Reporte generado: ${tickets.length} tickets`);
        mostrarOpciones.value = false;
    } catch (error) {
        console.error('Error al generar CSV:', error);
        toastHelper.error('Error al generar el reporte CSV');
    } finally {
        generandoReporte.value = false;
    }
};
</script>

<template>
    <div class="relative">
        <button @click="mostrarOpciones = !mostrarOpciones" :disabled="!evento.id"
            class="flex items-center gap-2 px-6 py-3 bg-[#B3224D] text-white font-semibold rounded-lg hover:bg-[#8d1a3c] transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed shadow-md">
            <FileDown :size="20" :stroke-width="2" />
            Generar Reporte de Tickets
        </button>

        <!-- Menú de opciones -->
        <div v-if="mostrarOpciones" @click.stop
            class="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50">
            <div class="p-2">
                <p class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                    Selecciona el formato
                </p>

                <button @click="generarExcel" :disabled="generandoReporte"
                    class="w-full flex items-center gap-3 px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors disabled:opacity-50">
                    <FileSpreadsheet :size="18" :stroke-width="2" class="text-green-600" />
                    <div>
                        <p class="font-medium">Excel (.xlsx)</p>
                        <p class="text-xs text-gray-500">Para análisis en Excel</p>
                    </div>
                </button>

                <button @click="generarCSV" :disabled="generandoReporte"
                    class="w-full flex items-center gap-3 px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors disabled:opacity-50">
                    <FileImage :size="18" :stroke-width="2" class="text-blue-600" />
                    <div>
                        <p class="font-medium">CSV (.csv)</p>
                        <p class="text-xs text-gray-500">Para Canva y diseño</p>
                    </div>
                </button>
            </div>
        </div>
    </div>

    <!-- Backdrop para cerrar el menú al hacer clic fuera -->
    <div v-if="mostrarOpciones" @click="mostrarOpciones = false" class="fixed inset-0 z-40"></div>

    <!-- Toast notifications -->
    <ToastNotification ref="toast" />
</template>
