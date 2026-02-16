<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { Eye, Edit, Trash2 } from "lucide-vue-next";

import TableTh from "@/components/Admin/TableTh.vue";
import TableTd from "@/components/Admin/TableTd.vue";
import ButtonMenu from "@/components/Admin/ButtonMenu.vue";
import Dropdown from "@/Helpers/Dropdown";
import MenuTable from "@/components/Admin/MenuTable.vue";
import Estado from "@/components/Admin/Estado.vue";

const props = defineProps({
    datos: {
        type: Array,
        required: true,
    },
    skeleton: {
        type: Boolean,
        default: true,
    },
    nSkeletons: {
        type: Number,
        default: 5,
    },
});

const authStore = useAuthStore();
const datos = computed(() => props.datos);

const { showDropdown, selectItem, menuX, menuY, abrirMenu, cerrarMenu } = Dropdown();

const emit = defineEmits(["editar", "eliminar"]);

const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

const getRoleBadgeColor = (rol) => {
    const colors = {
        ADMIN: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
        VENDEDOR: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
        VALIDADOR: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        CLIENTE: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
    };
    return colors[rol] || "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
};
</script>

<template>
    <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-transparent">
                    <tr>
                        <TableTh name="DNI" />
                        <TableTh name="Nombre Completo" />
                        <TableTh name="Email" />
                        <TableTh name="Teléfono" />
                        <TableTh name="Rol" />
                        <TableTh name="Estado" class="text-center" />
                        <TableTh name="Fecha Registro" />
                        <TableTh name="Acciones" class="text-center" />
                    </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    <tr v-if="skeleton" v-for="i in nSkeletons" :key="i"
                        class="hover:bg-gray-50 dark:hover:bg-gray-700/50 animate-pulse">
                        <TableTd colspan="8">
                            <div class="animate-pulse flex space-x-4 h-5 md:h-6"></div>
                        </TableTd>
                    </tr>

                    <tr v-else-if="!skeleton && datos.length === 0">
                        <TableTd colspan="8">
                            <div class="flex flex-col items-center justify-center space-y-2 py-20">
                                <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor"
                                    viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                                </svg>
                                <p class="text-sm font-medium text-gray-900 dark:text-white">
                                    No se encontraron clientes
                                </p>
                                <p class="text-xs text-gray-400">
                                    Intenta ajustar tus filtros o registrar un nuevo cliente.
                                </p>
                            </div>
                        </TableTd>
                    </tr>

                    <tr v-else v-for="dat in datos" :key="dat.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <TableTd class="whitespace-nowrap">
                            <span class="font-mono text-sm font-medium text-gray-900 dark:text-white">
                                {{ dat.dni }}
                            </span>
                        </TableTd>

                        <TableTd class="whitespace-nowrap">
                            <span class="font-medium text-gray-900 dark:text-white">
                                {{ dat.nombre_completo }}
                            </span>
                        </TableTd>

                        <TableTd class="whitespace-nowrap">
                            <span class="text-sm text-gray-600 dark:text-gray-400">
                                {{ dat.email || 'Sin email' }}
                            </span>
                        </TableTd>

                        <TableTd class="whitespace-nowrap">
                            <span class="text-sm text-gray-600 dark:text-gray-400">
                                {{ dat.telefono || 'Sin teléfono' }}
                            </span>
                        </TableTd>

                        <TableTd>
                            <span :class="getRoleBadgeColor(dat.rol)"
                                class="px-2 py-1 text-xs font-medium rounded-full">
                                {{ dat.rol || 'CLIENTE' }}
                            </span>
                        </TableTd>

                        <TableTd class="text-center">
                            <Estado :estado="dat.activo" />
                        </TableTd>

                        <TableTd class="whitespace-nowrap">
                            <span class="text-xs text-gray-500 dark:text-gray-400">
                                {{ formatFecha(dat.fecha_creacion) }}
                            </span>
                        </TableTd>

                        <TableTd class="text-center">
                            <div class="flex justify-center">
                                <button @click="abrirMenu(dat.id, $event)"
                                    class="text-gray-500 dark:text-gray-400 hover:text-primary-500">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                                    </svg>
                                </button>
                            </div>
                        </TableTd>
                    </tr>
                </tbody>
            </table>
        </div>

        <MenuTable :x="menuX" :y="menuY" :show="showDropdown && selectItem !== null" @close="cerrarMenu">
            <ButtonMenu :icon="Edit" name="Editar" @click="
                () => {
                    const cliente = datos.find(d => d.id === selectItem);
                    if (cliente) emit('editar', cliente);
                    cerrarMenu();
                }
            " />
            <ButtonMenu :icon="Trash2" name="Eliminar" @click="
                () => {
                    const cliente = datos.find(d => d.id === selectItem);
                    if (cliente) emit('eliminar', cliente);
                    cerrarMenu();
                }
            " />
        </MenuTable>

        <slot />
    </div>
</template>