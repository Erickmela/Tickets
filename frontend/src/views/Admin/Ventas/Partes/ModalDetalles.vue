<script setup>
import { ref, watch, computed } from "vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ToastNotification from "@/components/ToastNotification.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useVentasStore } from "@/stores/ventas";
import { dateTimeText, formatPrice } from "@/Helpers/Main";
import { 
    Calendar, 
    User, 
    CreditCard, 
    ShoppingBag, 
    Ticket as TicketIcon,
    MapPin,
    DollarSign,
    FileText,
    Clock
} from "lucide-vue-next";

const emit = defineEmits(["close"]);
const props = defineProps({
    show: {
        type: Boolean,
        default: false,
    },
    data: {
        type: Object,
        default: () => ({}),
    },
});

const ventasStore = useVentasStore();
const toastForm = ref(null);
const toastFormHelper = useToasts(toastForm);
const cargando = ref(false);
const detalleCompleto = ref(null);

const closeModal = () => {
    emit("close");
    detalleCompleto.value = null;
};

// Cargar detalles completos de la venta
const cargarDetalles = async () => {
    if (!props.data?.id) return;
    
    try {
        cargando.value = true;
        const response = await ventasStore.fetchVenta(props.data.id);
        detalleCompleto.value = response;
    } catch (error) {
        toastFormHelper.error('Error al cargar los detalles de la venta');
    } finally {
        cargando.value = false;
    }
};

// Agrupar tickets por zona
const ticketsPorZona = computed(() => {
    if (!detalleCompleto.value?.tickets) return [];
    
    const grupos = {};
    detalleCompleto.value.tickets.forEach(ticket => {
        const zonaNombre = ticket.zona?.nombre || 'Sin zona';
        if (!grupos[zonaNombre]) {
            grupos[zonaNombre] = {
                zona: ticket.zona,
                tickets: [],
                total: 0
            };
        }
        grupos[zonaNombre].tickets.push(ticket);
        grupos[zonaNombre].total += parseFloat(ticket.zona?.precio || 0);
    });
    
    return Object.entries(grupos).map(([nombre, data]) => ({
        nombre,
        ...data
    }));
});

// Método para obtener el color del estado
const getEstadoColor = (estado) => {
    const colores = {
        'DISPONIBLE': 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200',
        'USADO': 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-200',
        'ANULADO': 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200'
    };
    return colores[estado] || 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-200';
};

// Watch para cargar detalles cuando se abre el modal
watch(() => props.show, (isOpen) => {
    if (isOpen) {
        cargarDetalles();
    }
});
</script>

<template>
    <ToastNotification ref="toastForm" />
    <DialogModal :show="props.show" @close="closeModal" max-width="4xl">
        <template #title>
            <div class="flex items-center gap-2">
                <ShoppingBag class="w-6 h-6 text-primary-600" />
                <span>Detalles de la Venta #{{ props.data?.id }}</span>
            </div>
        </template>

        <template #content>
            <!-- Loading state -->
            <div v-if="cargando" class="flex justify-center items-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>

            <!-- Content -->
            <div v-else-if="detalleCompleto" class="space-y-6">
                <!-- Información general de la venta -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Cliente -->
                    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                        <div class="flex items-start gap-3">
                            <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                                <User class="w-5 h-5 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div class="flex-1">
                                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Cliente Pagador</h3>
                                <p class="text-base font-bold text-gray-900 dark:text-white">
                                    {{ detalleCompleto.cliente_pagador?.nombre_completo || 'N/A' }}
                                </p>
                                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    DNI: {{ detalleCompleto.cliente_pagador?.dni || 'N/A' }}
                                </p>
                                <p v-if="detalleCompleto.cliente_pagador?.telefono" class="text-sm text-gray-600 dark:text-gray-400">
                                    Tel: {{ detalleCompleto.cliente_pagador.telefono }}
                                </p>
                                <p v-if="detalleCompleto.cliente_pagador?.email" class="text-sm text-gray-600 dark:text-gray-400">
                                    Email: {{ detalleCompleto.cliente_pagador.email }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Vendedor -->
                    <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
                        <div class="flex items-start gap-3">
                            <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                                <User class="w-5 h-5 text-purple-600 dark:text-purple-400" />
                            </div>
                            <div class="flex-1">
                                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Vendedor</h3>
                                <p class="text-base font-bold text-gray-900 dark:text-white">
                                    {{ detalleCompleto.vendedor_nombre || 'N/A' }}
                                </p>
                                <div class="flex items-center gap-1 mt-2 text-xs text-gray-500 dark:text-gray-400">
                                    <Clock class="w-4 h-4" />
                                    <span>{{ dateTimeText(detalleCompleto.fecha_venta) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Método de pago y Total -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Método de pago -->
                    <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                        <div class="flex items-start gap-3">
                            <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                                <CreditCard class="w-5 h-5 text-green-600 dark:text-green-400" />
                            </div>
                            <div class="flex-1">
                                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Método de Pago</h3>
                                <p class="text-base font-bold text-gray-900 dark:text-white">
                                    {{ detalleCompleto.metodo_pago }}
                                </p>
                                <p v-if="detalleCompleto.nro_operacion" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    Operación: {{ detalleCompleto.nro_operacion }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Total -->
                    <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
                        <div class="flex items-start gap-3">
                            <div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                                <DollarSign class="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                            </div>
                            <div class="flex-1">
                                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Total Pagado</h3>
                                <p class="text-2xl font-bold text-green-600 dark:text-green-400">
                                    {{ formatPrice(detalleCompleto.total_pagado) }}
                                </p>
                                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    {{ detalleCompleto.cantidad_tickets }} ticket(s)
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Observaciones -->
                <div v-if="detalleCompleto.observaciones" class="bg-gray-50 dark:bg-gray-900/20 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <div class="flex items-start gap-3">
                        <div class="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                            <FileText class="w-5 h-5 text-gray-600 dark:text-gray-400" />
                        </div>
                        <div class="flex-1">
                            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Observaciones</h3>
                            <p class="text-sm text-gray-600 dark:text-gray-400">
                                {{ detalleCompleto.observaciones }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Tickets por zona -->
                <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
                    <div class="flex items-center gap-2 mb-4">
                        <TicketIcon class="w-5 h-5 text-primary-600" />
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Tickets Vendidos</h3>
                    </div>

                    <div class="space-y-4">
                        <div v-for="grupo in ticketsPorZona" :key="grupo.nombre" 
                            class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                            <!-- Cabecera de zona -->
                            <div class="bg-primary-50 dark:bg-primary-900/20 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-2">
                                        <MapPin class="w-4 h-4 text-primary-600" />
                                        <span class="font-semibold text-gray-900 dark:text-white">{{ grupo.nombre }}</span>
                                        <span class="text-sm text-gray-500 dark:text-gray-400">
                                            ({{ grupo.tickets.length }} ticket{{ grupo.tickets.length !== 1 ? 's' : '' }})
                                        </span>
                                    </div>
                                    <div class="text-sm font-semibold text-primary-600 dark:text-primary-400">
                                        {{ formatPrice(grupo.zona?.precio || 0) }} c/u
                                    </div>
                                </div>
                            </div>

                            <!-- Lista de tickets -->
                            <div class="divide-y divide-gray-200 dark:divide-gray-700">
                                <div v-for="ticket in grupo.tickets" :key="ticket.id" 
                                    class="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                                    <div class="flex items-center justify-between">
                                        <div class="flex-1">
                                            <div class="flex items-center gap-2 mb-1">
                                                <span class="text-sm font-medium text-gray-900 dark:text-white">
                                                    {{ ticket.nombre_titular }}
                                                </span>
                                                <span class="text-xs text-gray-500 dark:text-gray-400">
                                                    DNI: {{ ticket.dni_titular }}
                                                </span>
                                            </div>
                                            <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                                <span class="font-mono">{{ ticket.codigo_uuid }}</span>
                                            </div>
                                        </div>
                                        <div class="flex items-center gap-3">
                                            <span :class="['px-2 py-1 text-xs font-medium rounded-full', getEstadoColor(ticket.estado)]">
                                                {{ ticket.estado }}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Subtotal de zona -->
                            <div class="bg-gray-50 dark:bg-gray-900/50 px-4 py-2 border-t border-gray-200 dark:border-gray-700">
                                <div class="flex justify-between items-center text-sm">
                                    <span class="text-gray-600 dark:text-gray-400">Subtotal {{ grupo.nombre }}</span>
                                    <span class="font-semibold text-gray-900 dark:text-white">
                                        {{ formatPrice(grupo.total) }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Resumen final -->
                <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg p-4 border-2 border-primary-200 dark:border-primary-800">
                    <div class="flex justify-between items-center">
                        <span class="text-lg font-semibold text-gray-900 dark:text-white">Total de la Venta</span>
                        <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
                            {{ formatPrice(detalleCompleto.total_pagado) }}
                        </span>
                    </div>
                </div>
            </div>
        </template>

        <template #footer>
            <div class="flex justify-end">
                <ButtonCancel @click="closeModal" class="px-6">
                    Cerrar
                </ButtonCancel>
            </div>
        </template>
    </DialogModal>
</template>
