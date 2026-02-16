<script setup>
import { ref, onMounted, watch } from 'vue';
import AdmLayout from '@/Layouts/AdmLayout.vue';
import HeaderSecction from '@/components/Admin/Header.vue';
import Toolbar from '@/components/Admin/Toolbar.vue';
import Paginate from '@/components/Admin/Paginate.vue';
import Tabla from './Partes/Tabla.vue';
import ModalDetalle from './Partes/ModalDetalle.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import { useToasts } from '@/Helpers/useToasts';
import { ventasService } from '@/services/ventasService';
import { Ticket } from 'lucide-vue-next';

const toast = ref(null);
const toastHelper = useToasts(toast);

const tickets = ref([]);
const ticketSeleccionado = ref(null);
const mostrarModalDetalle = ref(false);
const skeleton = ref(false);
const paginate = ref({});

function getFormData() {
    return {
        page: 1,
        filterItemsPage: 10,
        filterSearch: '',
        filterEstado: ''
    };
}

const clearFilters = () => {
    form.value = getFormData();
};

const form = ref(getFormData());

const fetchDatos = async (p = form.value.page) => {
    form.value.page = p;
    if (skeleton.value) return;

    skeleton.value = true;
    try {
        const response = await ventasService.getTickets(
            form.value.page,
            form.value.filterItemsPage,
            form.value.filterSearch,
            form.value.filterEstado
        );

        tickets.value = response.results;
        paginate.value = {
            total: response.count,
            per_page: form.value.filterItemsPage,
            current_page: form.value.page,
            last_page: Math.ceil(response.count / form.value.filterItemsPage),
            from: response.results.length > 0 ? (form.value.page - 1) * form.value.filterItemsPage + 1 : 0,
            to: response.results.length > 0 ? (form.value.page - 1) * form.value.filterItemsPage + response.results.length : 0,
        };
    } catch (error) {
        console.error('Error al cargar tickets:', error);
        toastHelper.error('Error al cargar tickets', 'No se pudieron cargar los tickets');
        tickets.value = [];
        paginate.value = {};
    } finally {
        skeleton.value = false;
    }
};

const handleVerDetalle = async (ticket) => {
    try {
        // Obtener el ticket completo con todos los detalles
        const ticketCompleto = await ventasService.getTicket(ticket.id);
        ticketSeleccionado.value = ticketCompleto;
        mostrarModalDetalle.value = true;
    } catch (error) {
        console.error('Error al cargar detalle del ticket:', error);
        toastHelper.error('Error', 'No se pudo cargar el detalle del ticket');
    }
};

const handleCerrarDetalle = () => {
    mostrarModalDetalle.value = false;
    ticketSeleccionado.value = null;
};

const handlePageChange = (page) => {
    fetchDatos(page);
};

onMounted(() => {
    fetchDatos(1);
});

// Watch para items por página
watch([() => form.value.filterItemsPage], () => {
    fetchDatos(1);
});

// Watch para búsqueda con debounce
const debounceTimeout = ref(null);
watch(
    () => form.value.filterSearch,
    () => {
        clearTimeout(debounceTimeout.value);
        debounceTimeout.value = setTimeout(() => {
            fetchDatos(1);
        }, 700);
    }
);

// Watch para filtro de estado
watch(
    () => form.value.filterEstado,
    () => {
        fetchDatos(1);
    }
);
</script>

<template>
    <AdmLayout>
        <ToastNotification ref="toast" />

        <div class="space-y-6">
            <!-- Header -->
            <HeaderSecction 
                title="Tickets" 
                description="Gestión y consulta de tickets vendidos"
                :icon="Ticket"
            />

            <!-- Toolbar -->
            <Toolbar 
                @searchText="form.filterSearch = $event"
                @itemsPerPage="form.filterItemsPage = $event"
                :itemsPerPage="form.filterItemsPage" 
                :filterSearch="form.filterSearch" 
                placeholder="Buscar por DNI, nombre, código..."
            >
                <template #left-filters>
                    <select
                        v-model="form.filterEstado"
                        class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-primary-400 focus:border-primary-400 focus:outline-none"
                    >
                        <option value="">Todos los estados</option>
                        <option value="ACTIVO">Activos</option>
                        <option value="USADO">Usados</option>
                        <option value="ANULADO">Anulados</option>
                    </select>
                </template>
                <template #right-filters>
                    <button
                        @click="clearFilters"
                        class="p-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-none focus:border-primary-400"
                    >
                        <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                    </button>
                </template>
            </Toolbar>

            <!-- Tabla de tickets -->
            <Tabla
                :datos="tickets"
                :skeleton="skeleton"
                @ver-detalle="handleVerDetalle"
            >
                <Paginate 
                    :pagination="paginate" 
                    :skeleton="skeleton"
                    @page-changed="handlePageChange" 
                />
            </Tabla>
        </div>

        <!-- Modal Detalle -->
        <ModalDetalle
            v-if="mostrarModalDetalle"
            :ticket="ticketSeleccionado"
            @cerrar="handleCerrarDetalle"
        />
    </AdmLayout>
</template>
