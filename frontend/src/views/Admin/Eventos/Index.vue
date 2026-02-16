<script setup>
import { ref, onMounted, watch } from "vue";
import { useToasts } from "@/Helpers/useToasts";
import { useAuthStore } from "@/stores/auth";
import { useEventosStore } from "@/stores/eventos";
import { useRouter } from "vue-router";

import AdmLayout from "@/Layouts/AdmLayout.vue";
import Table from "./Partes/Tabla.vue";
import Toolbar from "@/components/Admin/Toolbar.vue";

import ModalEliminar from "./Partes/ModalEliminar.vue";
import Paginate from "@/components/Admin/Paginate.vue";
import HeaderSecction from "@/components/Admin/Header.vue";
import ToastNotification from "@/components/ToastNotification.vue";

const router = useRouter();
const toastGlobal = ref(null);
const toastGlobalHelper = useToasts(toastGlobal);

const authStore = useAuthStore();
const eventosStore = useEventosStore();

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

        const response = await eventosStore.fetchEventos(
            form.value.page,
            form.value.filterItemsPage,
            form.value.filterSearch
        );

        if (response.results) {
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
        toastGlobalHelper.error(error.response?.data?.message || 'Error al cargar eventos');
    } finally {
        setTimeout(() => {
            StateSkeleton.value = false;
        }, 500);
    }
};

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

// Navegar a crear evento
const crearEvento = () => {
    router.push({ name: 'admin-eventos-crear' });
};

// Navegar a editar evento
const editarEvento = (data) => {
    // Usar encoded_id si está disponible, si no usar id
    const slug = data.encoded_id || data.id;
    router.push({ name: 'admin-eventos-editar', params: { slug } });
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

// Navegar a zonas del evento
const verZonas = (evento) => {
    // Usar encoded_id si está disponible, si no usar id
    const slug = evento.encoded_id || evento.id;
    router.push(`/admin/eventos/${slug}/zonas`);
};
</script>

<template>
    <AdmLayout>
        <ToastNotification ref="toastGlobal" />

        <HeaderSecction title="Administración de Eventos"
            description="Gestiona y organiza todos los eventos del sistema">
            <template #actions>
                <button @click="crearEvento"
                    class="px-3 py-1.5 text-sm font-medium rounded-lg bg-primary-600 text-white hover:bg-primary-700 flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Nuevo Evento
                </button>
            </template>
        </HeaderSecction>

        <Toolbar @searchText="form.filterSearch = $event" @itemsPerPage="form.filterItemsPage = $event"
            :itemsPerPage="form.filterItemsPage" :filterSearch="form.filterSearch" placeholder="Buscar eventos...">
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
            </template>
        </Toolbar>

        <Table :datos="datos" :skeleton="StateSkeleton" @editar="editarEvento" @eliminar="openModalEliminar" 
            @ver-zonas="verZonas">
            <Paginate :pagination="paginate" :skeleton="StateSkeleton" @page-changed="fetchDatos" />
        </Table>
        <ModalEliminar :show="stateModalEliminar" :data="itemSelected" @data_destroyed="fetchDatos"
            @close="closeModalEliminar" />
    </AdmLayout>
</template>
