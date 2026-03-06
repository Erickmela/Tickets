<template>
    <AppLayout>
        <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
            <div class="max-w-2xl mx-auto">
                <!-- Loading State -->
                <div v-if="cargando" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
                    <Loader2 :size="64" class="mx-auto mb-6 text-[#B3224D] animate-spin" />
                    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                        Verificando pago...
                    </h2>
                    <p class="text-gray-600 dark:text-gray-400">
                        Estamos confirmando tu transacción con MercadoPago
                    </p>
                </div>

                <!-- Success State -->
                <div v-else-if="estadoPago === 'approved'" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
                    <div class="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                        <CheckCircle2 :size="48" class="text-green-600 dark:text-green-400" />
                    </div>
                    
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                        ¡Pago exitoso!
                    </h1>
                    
                    <p class="text-lg text-gray-600 dark:text-gray-400 mb-8">
                        Tu compra se ha procesado correctamente
                    </p>

                    <!-- Detalles del pago -->
                    <div class="bg-gray-50 dark:bg-gray-900/50 rounded-xl p-6 mb-8 text-left">
                        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4 uppercase tracking-wide">
                            Detalles de la transacción
                        </h3>
                        <div class="space-y-3">
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-600 dark:text-gray-400">ID de Pago:</span>
                                <span class="font-mono text-gray-900 dark:text-white">{{ paymentId }}</span>
                            </div>
                            <div v-if="detallesPago.medio_pago" class="flex justify-between text-sm">
                                <span class="text-gray-600 dark:text-gray-400">Método de pago:</span>
                                <span class="text-gray-900 dark:text-white capitalize">{{ detallesPago.medio_pago }}</span>
                            </div>
                            <div v-if="detallesPago.monto" class="flex justify-between text-sm">
                                <span class="text-gray-600 dark:text-gray-400">Monto:</span>
                                <span class="text-gray-900 dark:text-white font-bold">{{ detallesPago.monto }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-col sm:flex-row gap-4">
                        <RouterLink
                            to="/mis-tickets"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-[#B3224D] text-white rounded-xl font-semibold hover:bg-[#8d1a3c] transition-colors"
                        >
                            <Ticket :size="20" />
                            Ver mis tickets
                        </RouterLink>
                        <RouterLink
                            to="/eventos"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                            <Home :size="20" />
                            Ir al inicio
                        </RouterLink>
                    </div>
                </div>

                <!-- Pending State -->
                <div v-else-if="estadoPago === 'in_process' || estadoPago === 'pending'" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
                    <div class="w-20 h-20 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Clock :size="48" class="text-yellow-600 dark:text-yellow-400" />
                    </div>
                    
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                        Pago pendiente
                    </h1>
                    
                    <p class="text-lg text-gray-600 dark:text-gray-400 mb-8">
                        Tu pago está siendo procesado. Te notificaremos cuando se confirme.
                    </p>

                    <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 mb-8">
                        <p class="text-sm text-yellow-800 dark:text-yellow-300">
                            <strong>Importante:</strong> Algunos métodos de pago pueden tardar hasta 48 horas en confirmarse.
                            Recibirás un email cuando tu pago sea aprobado.
                        </p>
                    </div>

                    <div class="flex flex-col sm:flex-row gap-4">
                        <RouterLink
                            to="/mis-tickets"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-[#B3224D] text-white rounded-xl font-semibold hover:bg-[#8d1a3c] transition-colors"
                        >
                            <Ticket :size="20" />
                            Ver mis tickets
                        </RouterLink>
                        <RouterLink
                            to="/eventos"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                            <Home :size="20" />
                            Ir al inicio
                        </RouterLink>
                    </div>
                </div>

                <!-- Rejected State -->
                <div v-else-if="estadoPago === 'rejected' || estadoPago === 'cancelled'" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
                    <div class="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                        <XCircle :size="48" class="text-red-600 dark:text-red-400" />
                    </div>
                    
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                        Pago rechazado
                    </h1>
                    
                    <p class="text-lg text-gray-600 dark:text-gray-400 mb-8">
                        {{ mensajeError || 'No se pudo procesar tu pago' }}
                    </p>

                    <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-8">
                        <p class="text-sm text-red-800 dark:text-red-300">
                            Por favor, verifica que los datos de tu tarjeta sean correctos e intenta nuevamente.
                        </p>
                    </div>

                    <div class="flex flex-col sm:flex-row gap-4">
                        <RouterLink
                            to="/checkout"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-[#B3224D] text-white rounded-xl font-semibold hover:bg-[#8d1a3c] transition-colors"
                        >
                            <RotateCcw :size="20" />
                            Intentar nuevamente
                        </RouterLink>
                        <RouterLink
                            to="/eventos"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                            <Home :size="20" />
                            Ir al inicio
                        </RouterLink>
                    </div>
                </div>

                <!-- Error State -->
                <div v-else class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
                    <div class="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-6">
                        <AlertCircle :size="48" class="text-gray-600 dark:text-gray-400" />
                    </div>
                    
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                        No se pudo verificar el pago
                    </h1>
                    
                    <p class="text-lg text-gray-600 dark:text-gray-400 mb-8">
                        {{ mensajeError || 'Ocurrió un error al verificar el estado de tu pago' }}
                    </p>

                    <div class="flex flex-col sm:flex-row gap-4">
                        <button
                            @click="verificarPago"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-[#B3224D] text-white rounded-xl font-semibold hover:bg-[#8d1a3c] transition-colors"
                        >
                            <RotateCcw :size="20" />
                            Reintentar verificación
                        </button>
                        <RouterLink
                            to="/eventos"
                            class="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                            <Home :size="20" />
                            Ir al inicio
                        </RouterLink>
                    </div>
                </div>
            </div>
        </div>

        <!-- Toast Notification -->
        <ToastNotification ref="toastRef" />
    </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import AppLayout from '@/Layouts/AppLayout.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import { useToasts } from '@/Helpers/useToasts';
import mercadopagoService from '@/services/mercadopagoService';
import { clearCart } from '@/Helpers/cartState';
import {
    CheckCircle2,
    XCircle,
    Clock,
    AlertCircle,
    Loader2,
    Ticket,
    Home,
    RotateCcw
} from 'lucide-vue-next';

const route = useRoute();
const toastRef = ref(null);
const toast = useToasts(toastRef);

const cargando = ref(true);
const estadoPago = ref(null);
const paymentId = ref(null);
const detallesPago = ref({});
const mensajeError = ref(null);

// Verificar estado del pago
const verificarPago = async () => {
    cargando.value = true;
    mensajeError.value = null;

    try {
        // Obtener payment_id de la URL
        const urlParams = new URLSearchParams(window.location.search);
        paymentId.value = urlParams.get('payment_id');
        
        if (!paymentId.value) {
            throw new Error('No se encontró el ID de pago en la URL');
        }

        // Consultar estado del pago al backend
        const response = await mercadopagoService.consultarEstadoPago(paymentId.value);

        if (response.data.success) {
            estadoPago.value = response.data.status;
            detallesPago.value = {
                medio_pago: response.data.payment_method_id,
                monto: response.data.transaction_amount 
                    ? `S/ ${parseFloat(response.data.transaction_amount).toFixed(2)}` 
                    : null
            };

            // Si el pago fue aprobado, limpiar el carrito
            if (estadoPago.value === 'approved') {
                clearCart();
                toast.success('¡Pago exitoso!', 'Tu compra se ha procesado correctamente');
            } else if (estadoPago.value === 'in_process' || estadoPago.value === 'pending') {
                toast.info('Pago pendiente', 'Tu pago está siendo procesado');
            } else if (estadoPago.value === 'rejected' || estadoPago.value === 'cancelled') {
                mensajeError.value = response.data.status_detail || 'Tu pago fue rechazado';
                toast.error('Pago rechazado', mensajeError.value);
            }
        } else {
            throw new Error(response.data.error || 'No se pudo verificar el pago');
        }
    } catch (error) {
        console.error('Error al verificar pago:', error);
        mensajeError.value = error.response?.data?.error || error.message || 'Error al verificar el pago';
        toast.error('Error', mensajeError.value);
    } finally {
        cargando.value = false;
    }
};

onMounted(() => {
    verificarPago();
});
</script>

<style scoped>
.animate-spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
</style>
