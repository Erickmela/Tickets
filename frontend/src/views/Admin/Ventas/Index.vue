<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useToasts } from "@/Helpers/useToasts";
import { useAuthStore } from "@/stores/auth";
import { useVentasStore } from "@/stores/ventas";

import AdmLayout from "@/Layouts/AdmLayout.vue";
import Table from "./Partes/Tabla.vue";
import Toolbar from "@/components/Admin/Toolbar.vue";
import ModalEliminar from "./Partes/ModalEliminar.vue";
import ModalDetalles from "./Partes/ModalDetalles.vue";
import Paginate from "@/components/Admin/Paginate.vue";
import HeaderSecction from "@/components/Admin/Header.vue";
import ToastNotification from "@/components/ToastNotification.vue";

const router = useRouter();
const toastGlobal = ref(null);
const toastGlobalHelper = useToasts(toastGlobal);

const authStore = useAuthStore();
const ventasStore = useVentasStore();

const itemsxPage = ref(10);

function getFormData() {
    return {
        page: 1,
        filterItemsPage: itemsxPage.value,
        filterSearch: "",
    };
}

const clearFilters = () => {
    form.value = getFormData();
};

const form = ref(getFormData());

const paginate = ref({});
const datos = ref([]);
const StateSkeleton = ref(false);

const fetchDatos = async (p = form.value.page) => {
    form.value.page = p;
    if (StateSkeleton.value) return;

    try {
        StateSkeleton.value = true;
        datos.value = [];

        const response = await ventasStore.fetchVentas(
            form.value.page,
            form.value.filterItemsPage,
            form.value.filterSearch
        );

        // Manejar respuesta paginada de Django REST Framework
        if (response.results) {
            // Respuesta paginada
            datos.value = response.results;

            const totalPages = Math.ceil(response.count / form.value.filterItemsPage);
            const from = response.count > 0 ? ((form.value.page - 1) * form.value.filterItemsPage) + 1 : 0;
            const to = Math.min(form.value.page * form.value.filterItemsPage, response.count);

            paginate.value = {
                current_page: form.value.page,
                last_page: totalPages,
                from: from,
                to: to,
                total: response.count,
                count: response.count,
                next: response.next,
                previous: response.previous,
            };
        } else {
            // Respuesta sin paginar (fallback)
            datos.value = response;
            paginate.value = {
                current_page: 1,
                last_page: 1,
                from: 1,
                to: response.length,
                total: response.length,
                count: response.length,
                next: null,
                previous: null,
            };
        }
    } catch (error) {
        toastGlobalHelper.error(error.response?.data?.message || 'Error al cargar ventas');
    } finally {
        setTimeout(() => {
            StateSkeleton.value = false;
        }, 500);
    }
};

// Cargar datos iniciales
onMounted(() => {
    fetchDatos(1);
});

watch([() => form.value.filterItemsPage], () => {
    fetchDatos(1);
});

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

const itemSelected = ref(null);

// Modal Detalles
const stateModalDetalles = ref(false);
const openModalEditar = (data) => {
    stateModalDetalles.value = true;
    itemSelected.value = { ...data };
};
const closeModalDetalles = () => {
    stateModalDetalles.value = false;
    itemSelected.value = null;
};

// Modal Eliminar
const stateModalEliminar = ref(false);
const openModalEliminar = (data) => {
    stateModalEliminar.value = true;
    itemSelected.value = { ...data };
};
const closeModalEliminar = () => {
    stateModalEliminar.value = false;
    itemSelected.value = null;
};
</script>

<template>
    <AdmLayout>

        <ToastNotification ref="toastGlobal" />

        <!-- Cabecera mejorada -->
        <HeaderSecction title="Administración de Ventas" description="Gestiona y organiza todas las ventas de tickets">
            <template #actions>
                <button @click="router.push('/admin/ventas/crear')"
                    class="px-3 py-1.5 text-sm font-medium rounded-lg bg-primary-600 text-white hover:bg-primary-700 flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Nueva Venta
                </button>
            </template>
        </HeaderSecction>

        <!-- Barra de herramientas -->
        <Toolbar @searchText="form.filterSearch = $event" @itemsPerPage="form.filterItemsPage = $event"
            :itemsPerPage="form.filterItemsPage" :filterSearch="form.filterSearch" placeholder="Buscar ventas...">
            <template #left-filters> </template>
            <template #right-filters>
                <button @click="clearFilters"
                    class="p-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-none focus:border-primary-400">
                    <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                </button>

                <button
                    class="p-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-none focus:border-primary-400">
                    <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
              Detalles :show="stateModalDetalles" :data="itemSelected" @close="closeModalDetalles" />

        <Modal          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                </button>
            </template>
        </Toolbar>

        <Table :datos="datos" :skeleton="StateSkeleton" @editar="openModalEditar" @eliminar="openModalEliminar">
            <Paginate :pagination="paginate" :skeleton="StateSkeleton" @page-changed="fetchDatos" />
        </Table>

        <ModalEliminar :show="stateModalEliminar" :data="itemSelected" @data_destroyed="fetchDatos"
            @close="closeModalEliminar" />
    </AdmLayout>
</template>
