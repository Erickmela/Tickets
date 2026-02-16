<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { dateTimeText } from "@/helpers/Main";
import { Eye, Edit, Trash2 } from "lucide-vue-next";

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

const emit = defineEmits(["editar", "eliminar", "ver-zonas"]);

const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

const formatHora = (hora) => {
    if (!hora) return '-';
    return hora;
};
</script>

<template>
    <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-transparent">
                    <tr>
                        <TableTh name="Nombre" />
                        <TableTh name="Fecha" />
                        <TableTh name="Hora" />
                        <TableTh name="Lugar" />
                        <TableTh name="Capacidad Total" class="text-center" />
                        <TableTh name="Vendidos" class="text-center" />
                        <TableTh name="Estado" class="text-center" />
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
                                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                <p class="text-sm font-medium text-gray-900 dark:text-white">
                                    No se encontraron eventos
                                </p>
                                <p class="text-xs text-gray-400">
                                    Intenta ajustar tus filtros o crear un nuevo evento.
                                </p>
                            </div>
                        </TableTd>
                    </tr>

                    <tr v-else v-for="dat in datos" :key="dat.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <TableTd class="whitespace-nowrap">
                            <div class="flex flex-col">
                                <span class="font-medium text-gray-900 dark:text-white">
                                    {{ dat.nombre }}
                                </span>
                                <span v-if="dat.descripcion" class="text-xs text-gray-500 dark:text-gray-400">
                                    {{ dat.descripcion }}
                                </span>
                            </div>
                        </TableTd>

                        <TableTd :contend="formatFecha(dat.fecha)" class="whitespace-nowrap" />

                        <TableTd :contend="formatHora(dat.hora_inicio)" class="whitespace-nowrap" />

                        <TableTd :contend="dat.lugar" class="whitespace-nowrap" />

                        <TableTd class="text-center">
                            <span class="font-semibold text-gray-900 dark:text-white">
                                {{ dat.capacidad_total || 0 }}
                            </span>
                        </TableTd>

                        <TableTd class="text-center">
                            <div class="flex flex-col items-center">
                                <span class="font-semibold text-gray-900 dark:text-white">
                                    {{ dat.tickets_vendidos || 0 }}
                                </span>
                                <span v-if="dat.capacidad_total > 0" class="text-xs text-gray-500 dark:text-gray-400">
                                    {{ Math.round((dat.tickets_vendidos / dat.capacidad_total) * 100) }}%
                                </span>
                            </div>
                        </TableTd>

                        <TableTd class="text-center">
                            <span :class="[
                                'px-2 py-1 text-xs font-medium rounded-full',
                                dat.estado === '2'
                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                    : dat.estado === '3'
                                        ? 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                            ]">
                                {{ dat.estado === '1' ? 'PRÓXIMO' : dat.estado === '2' ? 'ACTIVO' : 'FINALIZADO' }}
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
            <ButtonMenu :icon="Eye" name="Ver Zonas" @click="
                () => {
                    const evento = datos.find(d => d.id === selectItem);
                    if (evento) emit('ver-zonas', evento);
                    cerrarMenu();
                }
            " />
            <ButtonMenu :icon="Edit" name="Editar" @click="
                () => {
                    const evento = datos.find(d => d.id === selectItem);
                    if (evento) emit('editar', evento);
                    cerrarMenu();
                }
            " />
            <ButtonMenu :icon="Trash2" name="Eliminar" @click="
                () => {
                    const evento = datos.find(d => d.id === selectItem);
                    if (evento) emit('eliminar', evento);
                    cerrarMenu();
                }
            " />
        </MenuTable>

        <slot />
    </div>
</template>
