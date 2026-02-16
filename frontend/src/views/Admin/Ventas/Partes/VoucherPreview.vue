<script setup>
import { computed } from "vue";
import { Calendar, MapPin, Ticket, CreditCard, User } from "lucide-vue-next";

const props = defineProps({
    formData: {
        type: Object,
        default: () => null
    },
    isValid: {
        type: Boolean,
        default: false
    }
});

const hasData = computed(() => props.formData !== null);

const tickets = computed(() => {
    if (!props.formData) return [];
    return props.formData.tickets.map(ticket => {
        const zona = props.formData.zonas?.find(z => z.id === parseInt(ticket.zona_id));
        return {
            ...ticket,
            zona_nombre: zona?.nombre || 'Sin seleccionar',
            zona_precio: zona?.precio || 0,
            evento_nombre: zona?.evento_nombre || props.formData.evento?.nombre || 'Evento',
        };
    });
});

const eventoInfo = computed(() => {
    if (!props.formData?.evento) return null;
    return props.formData.evento;
});

const ticketsValidos = computed(() => {
    return tickets.value.filter(t => t.zona_id && t.dni_titular && t.nombre_titular);
});

const totalVenta = computed(() => {
    return props.formData?.total || 0;
});

const metodoPagoLabel = computed(() => {
    const metodos = {
        'EFECTIVO': 'Efectivo',
        'TRANSFERENCIA': 'Transferencia',
        'YAPE': 'Yape',
        'PLIN': 'Plin',
        'TARJETA': 'Tarjeta'
    };
    return metodos[props.formData?.metodo_pago] || 'No seleccionado';
});

const fechaActual = computed(() => {
    return new Date().toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
});
</script>

<template>
    <div class="space-y-4">
        <!-- Header del preview -->
        <div class="bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg shadow-lg p-6 text-white">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-bold">Vista Previa</h3>
                <div :class="[
                    'px-3 py-1 rounded-full text-xs font-semibold',
                    isValid ? 'bg-green-500' : 'bg-yellow-500/30'
                ]">
                    {{ isValid ? '✓ Completo' : 'Incompleto' }}
                </div>
            </div>
            <p class="text-sm text-primary-100">
                Los datos se actualizarán automáticamente mientras completas el formulario
            </p>
        </div>

        <!-- Resumen de la Venta -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <!-- Información del Evento -->
            <div v-if="eventoInfo"
                class="p-4 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/30 dark:to-primary-800/30 border-b border-primary-200 dark:border-primary-700">
                <div class="flex items-center gap-2 mb-2">
                    <Calendar class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    <h4 class="font-semibold text-gray-900 dark:text-white">Evento</h4>
                </div>
                <div class="space-y-1 text-sm">
                    <p class="font-bold text-primary-700 dark:text-primary-300">
                        {{ eventoInfo.nombre }}
                    </p>
                    <p v-if="eventoInfo.fecha" class="text-gray-600 dark:text-gray-400">
                        📅 {{ new Date(eventoInfo.fecha).toLocaleDateString('es-PE', {
                            year: 'numeric', month: 'long',
                        day: 'numeric' }) }}
                    </p>
                    <p v-if="eventoInfo.hora" class="text-gray-600 dark:text-gray-400">
                        🕐 {{ eventoInfo.hora }}
                    </p>
                    <p v-if="eventoInfo.lugar" class="text-gray-600 dark:text-gray-400">
                        📍 {{ eventoInfo.lugar }}
                    </p>
                </div>
            </div>

            <!-- Datos del Cliente -->
            <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-2 mb-3">
                    <User class="w-5 h-5 text-primary-500" />
                    <h4 class="font-semibold text-gray-900 dark:text-white">Cliente</h4>
                </div>
                <div v-if="hasData && formData.cliente_dni" class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-500 dark:text-gray-400">DNI:</span>
                        <span class="font-medium text-gray-900 dark:text-white">
                            {{ formData.cliente_dni || '-' }}
                        </span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-500 dark:text-gray-400">Nombre:</span>
                        <span class="font-medium text-gray-900 dark:text-white">
                            {{ formData.cliente_nombre || '-' }}
                        </span>
                    </div>
                    <div v-if="formData.cliente_telefono" class="flex justify-between">
                        <span class="text-gray-500 dark:text-gray-400">Teléfono:</span>
                        <span class="font-medium text-gray-900 dark:text-white">
                            {{ formData.cliente_telefono }}
                        </span>
                    </div>
                </div>
                <div v-else class="text-sm text-gray-400 italic">
                    Ingrese los datos del cliente
                </div>
            </div>

            <!-- Tickets -->
            <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-2 mb-3">
                    <Ticket class="w-5 h-5 text-primary-500" />
                    <h4 class="font-semibold text-gray-900 dark:text-white">
                        Tickets ({{ ticketsValidos.length }})
                    </h4>
                </div>

                <div v-if="ticketsValidos.length > 0" class="space-y-3">
                    <div v-for="(ticket, index) in ticketsValidos" :key="index"
                        class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                        <div class="flex justify-between items-start mb-2">
                            <div class="flex-1">
                                <p class="font-semibold text-gray-900 dark:text-white text-sm">
                                    {{ ticket.zona_nombre }}
                                </p>
                                <p class="text-xs text-gray-500 dark:text-gray-400">
                                    {{ ticket.nombre_titular }}
                                </p>
                                <p class="text-xs text-gray-400 dark:text-gray-500">
                                    DNI: {{ ticket.dni_titular }}
                                </p>
                            </div>
                            <span class="text-sm font-bold text-primary-600 dark:text-primary-400">
                                S/ {{ parseFloat(ticket.zona_precio).toFixed(2) }}
                            </span>
                        </div>
                    </div>
                </div>

                <div v-else class="text-sm text-gray-400 italic">
                    No hay tickets agregados
                </div>
            </div>

            <!-- Método de Pago -->
            <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-2 mb-3">
                    <CreditCard class="w-5 h-5 text-primary-500" />
                    <h4 class="font-semibold text-gray-900 dark:text-white">Pago</h4>
                </div>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-500 dark:text-gray-400">Método:</span>
                        <span class="font-medium text-gray-900 dark:text-white">
                            {{ metodoPagoLabel }}
                        </span>
                    </div>
                    <div v-if="formData?.nro_operacion" class="flex justify-between">
                        <span class="text-gray-500 dark:text-gray-400">N° Operación:</span>
                        <span class="font-medium text-gray-900 dark:text-white">
                            {{ formData.nro_operacion }}
                        </span>
                    </div>
                </div>
            </div>

            <!-- Total -->
            <div class="p-4 bg-gray-50 dark:bg-gray-700">
                <div class="flex justify-between items-center">
                    <span class="text-lg font-semibold text-gray-900 dark:text-white">Total:</span>
                    <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
                        S/ {{ totalVenta.toFixed(2) }}
                    </span>
                </div>
            </div>
        </div>

        <!-- Info adicional -->
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="flex gap-3">
                <svg class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-sm text-blue-700 dark:text-blue-300">
                    <p class="font-medium mb-1">Información</p>
                    <ul class="list-disc list-inside space-y-1 text-xs">
                        <li>Los códigos QR se generarán automáticamente</li>
                        <li>El cliente recibirá sus tickets por email</li>
                        <li>Máximo 3 tickets por venta</li>
                        <li>Cada titular puede tener máximo 3 tickets por evento</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Fecha -->
        <div class="text-center text-xs text-gray-400 dark:text-gray-500">
            {{ fechaActual }}
        </div>
    </div>
</template>
