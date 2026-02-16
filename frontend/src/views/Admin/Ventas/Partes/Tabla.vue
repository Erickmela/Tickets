<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { hasPermission, dateTimeText, formatPrice } from "@/helpers/Main";

import TableTh from "@/components/Admin/TableTh.vue";
import TableTd from "@/components/Admin/TableTd.vue";
import ButtonMenu from "@/components/Admin/ButtonMenu.vue";
import Dropdown from "@/helpers/Dropdown";
import MenuTable from "@/components/Admin/MenuTable.vue";

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
</script>

<template>
    <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-transparent">
                    <tr>
                        <TableTh name="ID" />
                        <TableTh name="Cliente" />
                        <TableTh name="Vendedor" />
                        <TableTh name="Total" />
                        <TableTh name="Tickets" class="text-center" />
                        <TableTh name="Método Pago" />
                        <TableTh name="Fecha" />
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

                    <!-- Sin datos -->
                    <tr v-else-if="!skeleton && datos.length === 0">
                        <TableTd colspan="8">
                            <div class="flex flex-col items-center justify-center space-y-2 py-20">
                                <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor"
                                    viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2zM10 8.5a.5.5 0 11-1 0 .5.5 0 011 0zm5 5a.5.5 0 11-1 0 .5.5 0 011 0z" />
                                </svg>
                                <p class="text-sm font-medium text-gray-900 dark:text-white">
                                    No se encontraron ventas
                                </p>
                                <p class="text-xs text-gray-400">
                                    Intenta ajustar tus filtros o crear una nueva venta.
                                </p>
                            </div>
                        </TableTd>
                    </tr>

                    <tr v-else v-for="dat in datos" :key="dat.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <TableTd :contend="'#' + dat.id" class="whitespace-nowrap font-medium" />

                        <TableTd>
                            <div>
                                <div class="text-sm font-medium text-gray-900 dark:text-white">
                                    {{ dat.cliente_nombre }}
                                </div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    DNI: {{ dat.cliente_dni || 'N/A' }}
                                </div>
                            </div>
                        </TableTd>

                        <TableTd>
                            <div class="text-sm text-gray-900 dark:text-white">
                                {{ dat.vendedor_nombre }}
                            </div>
                        </TableTd>

                        <TableTd>
                            <div class="text-sm font-semibold text-green-600 dark:text-green-400">
                                {{ formatPrice(dat.total_pagado) }}
                            </div>
                        </TableTd>

                        <TableTd class="whitespace-nowrap text-center">
                            <span
                                class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                {{ dat.cantidad_tickets }} tickets
                            </span>
                        </TableTd>

                        <TableTd>
                            <span
                                class="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                                {{ dat.metodo_pago }}
                            </span>
                        </TableTd>

                        <TableTd class="whitespace-nowrap">
                            <div class="text-xs text-gray-500 dark:text-gray-400">
                                {{ dateTimeText(dat.fecha_venta) }}
                            </div>
                        </TableTd>

                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div class="flex justify-center space-x-3">
                                <button @click="$emit('editar', dat)"
                                    class="text-gray-500 dark:text-gray-400 hover:text-primary-500"
                                    title="Ver detalles">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                    </svg>
                                </button>
                                <button v-if="hasPermission('anular_ventas', authStore.userRole)"
                                    @click="abrirMenu(dat, $event)"
                                    class="text-gray-500 dark:text-gray-400 hover:text-primary-500">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                                    </svg>
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <MenuTable :x="menuX" :y="menuY" :show="showDropdown" @close="cerrarMenu">
                <ButtonMenu name="Anular Venta" @click="emit('eliminar', selectItem)" />
            </MenuTable>
        </div>

        <!-- Paginate -->
        <slot />
    </div>
</template>
