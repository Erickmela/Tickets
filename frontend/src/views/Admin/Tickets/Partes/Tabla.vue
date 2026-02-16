<script setup>
import { computed } from 'vue';
import { Eye } from 'lucide-vue-next';

import TableTh from '@/components/Admin/TableTh.vue';
import TableTd from '@/components/Admin/TableTd.vue';
import ButtonMenu from '@/components/Admin/ButtonMenu.vue';
import Dropdown from '@/helpers/Dropdown';
import MenuTable from '@/components/Admin/MenuTable.vue';

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

const datos = computed(() => props.datos);
const { showDropdown, selectItem, menuX, menuY, abrirMenu, cerrarMenu } = Dropdown();

const emit = defineEmits(['ver-detalle']);

const getEstadoBadgeClass = (estado) => {
    const classes = {
        ACTIVO: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        USADO: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        ANULADO: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
    };
    return classes[estado] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
};

const getEstadoTexto = (estado) => {
    const textos = {
        ACTIVO: 'ACTIVO',
        USADO: 'USADO',
        ANULADO: 'ANULADO'
    };
    return textos[estado] || estado;
};

const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};
</script>

<template>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-transparent">
                    <tr>
                        <TableTh name="Ticket" />
                        <TableTh name="Titular" />
                        <TableTh name="Evento / Zona" />
                        <TableTh name="Estado" class="text-center" />
                        <TableTh name="Fecha Emisión" />
                        <TableTh name="Acciones" class="text-center" />
                    </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    <!-- Skeleton loading -->
                    <tr v-if="skeleton" v-for="i in nSkeletons" :key="i"
                        class="hover:bg-gray-50 dark:hover:bg-gray-700/50 animate-pulse">
                        <TableTd colspan="6">
                            <div class="animate-pulse flex space-x-4 h-5 md:h-6"></div>
                        </TableTd>
                    </tr>

                    <!-- Sin resultados -->
                    <tr v-else-if="!skeleton && datos.length === 0">
                        <TableTd colspan="6">
                            <div class="flex flex-col items-center justify-center space-y-2 py-20">
                                <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor"
                                    viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
                                </svg>
                                <p class="text-sm font-medium text-gray-900 dark:text-white">
                                    No se encontraron tickets
                                </p>
                                <p class="text-xs text-gray-400">
                                    Intenta ajustar tus filtros o crea una nueva venta.
                                </p>
                            </div>
                        </TableTd>
                    </tr>

                    <!-- Datos -->
                    <tr v-else v-for="dat in datos" :key="dat.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <!-- Código Ticket -->
                        <TableTd class="whitespace-nowrap">
                            <div class="flex flex-col">
                                <span class="font-medium text-gray-900 dark:text-white">
                                    #{{ dat.id }}
                                </span>
                            </div>
                        </TableTd>

                        <!-- Titular -->
                        <TableTd class="whitespace-nowrap">
                            <div class="flex flex-col">
                                <span class="font-medium text-gray-900 dark:text-white">
                                    {{ dat.nombre_titular }}
                                </span>
                                <span class="text-xs text-gray-500 dark:text-gray-400">
                                    DNI: {{ dat.dni_titular }}
                                </span>
                            </div>
                        </TableTd>

                        <!-- Evento / Zona -->
                        <TableTd>
                            <div class="flex flex-col">
                                <span class="font-medium text-gray-900 dark:text-white">
                                    {{ dat.evento_nombre || '-' }}
                                </span>
                                <span class="text-xs text-gray-500 dark:text-gray-400">
                                    {{ dat.zona_nombre || '-' }}
                                </span>
                            </div>
                        </TableTd>

                        <!-- Estado -->
                        <TableTd class="text-center">
                            <span :class="[
                                'px-2 py-1 text-xs font-medium rounded-full',
                                getEstadoBadgeClass(dat.estado)
                            ]">
                                {{ getEstadoTexto(dat.estado) }}
                            </span>
                        </TableTd>

                        <!-- Fecha -->
                        <TableTd :contend="formatFecha(dat.fecha_creacion)" class="whitespace-nowrap" />

                        <!-- Acciones -->
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
            <ButtonMenu :icon="Eye" name="Ver Detalles" @click="
                () => {
                    const ticket = datos.find(d => d.id === selectItem);
                    if (ticket) emit('ver-detalle', ticket);
                    cerrarMenu();
                }
            " />
        </MenuTable>

        <slot />
    </div>
</template>
