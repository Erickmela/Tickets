<script setup>
import { ref, onMounted, watch } from "vue";
import { useUsuariosStore } from "@/stores/usuarios";
import { useToasts } from "@/Helpers/useToasts";
import AdmLayout from "@/Layouts/AdmLayout.vue";
import Tabla from "./Partes/Tabla.vue";
import ModalAgregar from "./Partes/ModalAgregar.vue";
import ModalEditar from "./Partes/ModalEditar.vue";
import ModalEliminar from "./Partes/ModalEliminar.vue";
import Toolbar from "@/components/Admin/Toolbar.vue";
import Paginate from "@/components/Admin/Paginate.vue";
import HeaderSecction from "@/components/Admin/Header.vue";
import ToastNotification from "@/components/ToastNotification.vue";

const usuariosStore = useUsuariosStore();

const toast = ref(null);
const toastHelper = useToasts(toast);

const stateModalCrear = ref(false);
const stateModalEditar = ref(false);
const stateModalEliminar = ref(false);

const trabajadorSeleccionado = ref(null);

const itemsPerPage = ref(10);

function getFormData() {
    return {
        page: 1,
        filterItemsPage: itemsPerPage.value,
        filterSearch: "",
    };
}

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

        const response = await usuariosStore.fetchTrabajadores(
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
        toastHelper.error(error.response?.data?.message || 'Error al cargar trabajadores');
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

// Modal Crear
const openModalCrear = () => {
    stateModalCrear.value = true;
};

const closeModalCrear = () => {
    stateModalCrear.value = false;
    trabajadorSeleccionado.value = null;
};

const handleDataCreated = async () => {
    toastHelper.success("Trabajador creado correctamente");
    await fetchDatos(form.value.page);
};

// Modal Editar
const openModalEditar = (trabajador) => {
    trabajadorSeleccionado.value = { ...trabajador };
    stateModalEditar.value = true;
};

const closeModalEditar = () => {
    stateModalEditar.value = false;
    trabajadorSeleccionado.value = null;
};

const handleDataUpdated = async () => {
    toastHelper.success("Trabajador actualizado correctamente");
    await fetchDatos(form.value.page);
};

// Modal Eliminar
const openModalEliminar = (trabajador) => {
    trabajadorSeleccionado.value = { ...trabajador };
    stateModalEliminar.value = true;
};

const closeModalEliminar = () => {
    stateModalEliminar.value = false;
    trabajadorSeleccionado.value = null;
};

const handleDataDestroyed = async () => {
    toastHelper.success("Trabajador eliminado correctamente");
    await fetchDatos(form.value.page);
};

const handleToggleEstado = async (trabajador) => {
    try {
        await usuariosStore.toggleTrabajadorActivo(trabajador.id);
        toastHelper.success(`Trabajador ${trabajador.activo ? 'desactivado' : 'activado'} correctamente`);
        await fetchDatos(form.value.page);
    } catch (error) {
        toastHelper.error("Error al cambiar el estado del trabajador");
    }
};
</script>

<template>
    <AdmLayout title="Trabajadores">
        <ToastNotification ref="toast" />

        <HeaderSecction title="Gestión de Trabajadores" description="Gestiona todos los trabajadores del sistema">
            <template #actions>
                <button @click="openModalCrear"
                    class="px-3 py-1.5 text-sm font-medium rounded-lg bg-primary-600 text-white hover:bg-primary-700 flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Nuevo Trabajador
                </button>
            </template>
        </HeaderSecction>

        <Toolbar @searchText="form.filterSearch = $event" @itemsPerPage="form.filterItemsPage = $event"
            :itemsPerPage="form.filterItemsPage" :filterSearch="form.filterSearch"
            placeholder="Buscar trabajadores por DNI, nombre o usuario...">
            <template #left-filters> </template>
            <template #right-filters>
                <button @click="form.filterSearch = ''; fetchDatos(1)"
                    class="p-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-none focus:border-primary-400">
                    <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                </button>
            </template>
        </Toolbar>

        <Tabla :datos="datos" :skeleton="StateSkeleton" @editar="openModalEditar" @eliminar="openModalEliminar"
            @toggleEstado="handleToggleEstado">
            <Paginate :pagination="paginate" :skeleton="StateSkeleton" @page-changed="fetchDatos" />
        </Tabla>

        <ModalAgregar :show="stateModalCrear" @close="closeModalCrear" @data_created="handleDataCreated" />

        <ModalEditar :show="stateModalEditar" :data="trabajadorSeleccionado" @close="closeModalEditar"
            @data_updated="handleDataUpdated" />

        <ModalEliminar :show="stateModalEliminar" :data="trabajadorSeleccionado" @close="closeModalEliminar"
            @data_destroyed="handleDataDestroyed" />
    </AdmLayout>
</template>
