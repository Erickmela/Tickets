<script setup>
import { computed } from 'vue';
import DialogModal from '@/components/DialogModal.vue';
import { X, QrCode, User, MapPin, Calendar, Hash } from 'lucide-vue-next';

const props = defineProps({
    ticket: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['cerrar']);

const handleCerrar = () => {
    emit('cerrar');
};

const getEstadoBadgeClass = (estado) => {
    const classes = {
        ACTIVO: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
        USADO: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
        ANULADO: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
    };
    return classes[estado] || 'bg-gray-100 text-gray-800';
};

const getEstadoTexto = (estado) => {
    const textos = {
        ACTIVO: 'Activo',
        USADO: 'Usado',
        ANULADO: 'Anulado'
    };
    return textos[estado] || estado;
};

const qrImageUrl = computed(() => {
    // Priorizar qr_image_url que viene del serializer con URL completa
    if (props.ticket?.qr_image_url) {
        return props.ticket.qr_image_url;
    }
    
    // Fallback: construir URL manualmente desde qr_image
    if (props.ticket?.qr_image) {
        const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';
        return `${baseUrl}/media/${props.ticket.qr_image}`;
    }
    
    return null;
});
</script>

<template>
    <DialogModal :show="true" @close="handleCerrar" max-width="2xl">
        <template #title>
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="p-2 bg-[#B3224D] rounded-lg">
                        <QrCode class="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                            Detalles del Ticket
                        </h3>
                        <p class="text-sm text-gray-500 dark:text-gray-400">
                            Ticket #{{ ticket.id }}
                        </p>
                    </div>
                </div>
                <button
                    @click="handleCerrar"
                    class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                    <X class="w-5 h-5" />
                </button>
            </div>
        </template>

        <template #content>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Columna izquierda: Información del ticket -->
                <div class="space-y-4">
                    <!-- Estado -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Estado
                        </label>
                        <span
                            :class="getEstadoBadgeClass(ticket.estado)"
                            class="inline-block px-3 py-1 text-sm font-medium rounded-full"
                        >
                            {{ getEstadoTexto(ticket.estado) }}
                        </span>
                    </div>

                    <!-- Código UUID -->
                    <div>
                        <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            <Hash class="w-4 h-4" />
                            Código UUID
                        </label>
                        <p class="text-sm text-gray-900 dark:text-white font-mono bg-gray-50 dark:bg-gray-700 p-2 rounded break-all">
                            {{ ticket.codigo_uuid }}
                        </p>
                    </div>

                    <!-- Titular -->
                    <div>
                        <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            <User class="w-4 h-4" />
                            Titular
                        </label>
                        <div class="space-y-1">
                            <p class="text-sm text-gray-900 dark:text-white font-medium">
                                {{ ticket.nombre_titular }}
                            </p>
                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                DNI: {{ ticket.dni_titular }}
                            </p>
                        </div>
                    </div>

                    <!-- Evento y Zona -->
                    <div>
                        <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            <MapPin class="w-4 h-4" />
                            Evento / Zona
                        </label>
                        <div class="space-y-1">
                            <p class="text-sm text-gray-900 dark:text-white font-medium">
                                {{ ticket.zona?.evento?.nombre || '-' }}
                            </p>
                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                Zona: {{ ticket.zona?.nombre || '-' }}
                            </p>
                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                Precio: S/ {{ ticket.zona?.precio || '0.00' }}
                            </p>
                        </div>
                    </div>

                    <!-- Fechas -->
                    <div>
                        <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            <Calendar class="w-4 h-4" />
                            Fechas
                        </label>
                        <div class="space-y-1">
                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                <span class="font-medium">Emisión:</span>
                                {{ new Date(ticket.fecha_creacion).toLocaleString('es-PE') }}
                            </p>
                            <p v-if="ticket.fecha_actualizacion" class="text-sm text-gray-500 dark:text-gray-400">
                                <span class="font-medium">Actualización:</span>
                                {{ new Date(ticket.fecha_actualizacion).toLocaleString('es-PE') }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Columna derecha: Código QR -->
                <div class="flex flex-col items-center justify-center space-y-4 bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                    <div class="text-center">
                        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Código QR
                        </h4>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mb-4">
                            Escanear para validar ingreso
                        </p>
                    </div>

                    <!-- QR Code -->
                    <div v-if="qrImageUrl" class="bg-white p-4 rounded-lg shadow-sm">
                        <img
                            :src="qrImageUrl"
                            :alt="`QR Ticket ${ticket.id}`"
                            class="w-64 h-64 object-contain"
                        />
                    </div>
                    <div v-else class="w-64 h-64 flex items-center justify-center bg-gray-200 dark:bg-gray-600 rounded-lg">
                        <p class="text-sm text-gray-500 dark:text-gray-400">
                            QR no disponible
                        </p>
                    </div>

                    <!-- Botón descargar (opcional) -->
                    <button
                        v-if="qrImageUrl"
                        @click="window.open(qrImageUrl, '_blank')"
                        class="px-4 py-2 bg-[#B3224D] text-white rounded-lg hover:bg-[#8d1a3c] transition-colors text-sm"
                    >
                        Descargar QR
                    </button>
                </div>
            </div>

            <!-- Información de validación (si está usado) -->
            <div v-if="ticket.estado === 'USADO' && ticket.validaciones?.length > 0"
                 class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <h4 class="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
                    Información de validación
                </h4>
                <div class="space-y-1 text-sm text-blue-800 dark:text-blue-400">
                    <p>
                        <span class="font-medium">Fecha de ingreso:</span>
                        {{ new Date(ticket.validaciones[0].fecha_hora_ingreso).toLocaleString('es-PE') }}
                    </p>
                    <p v-if="ticket.validaciones[0].validador">
                        <span class="font-medium">Validado por:</span>
                        {{ ticket.validaciones[0].validador.nombre_completo || 'N/A' }}
                    </p>
                </div>
            </div>
        </template>

        <template #footer>
            <div class="flex justify-end">
                <button
                    @click="handleCerrar"
                    class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                    Cerrar
                </button>
            </div>
        </template>
    </DialogModal>
</template>
