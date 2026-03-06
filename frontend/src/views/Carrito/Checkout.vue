<template>
    <AppLayout title="Checkout">
        <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
            <div class="container mx-auto px-4 max-w-4xl">
                <!-- Header -->
                <div class="mb-8">
                    <RouterLink
                        to="/carrito"
                        class="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-[#B3224D] mb-4 transition-colors"
                    >
                        <ArrowLeft :size="20" />
                        Volver al carrito
                    </RouterLink>
                    <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
                        💳 Finalizar Compra
                    </h1>
                    <p class="text-gray-600 dark:text-gray-400">
                        Completa tu pedido y disfruta de tus eventos
                    </p>
                </div>

                <div class="grid lg:grid-cols-3 gap-8">
                    <!-- Formulario de pago -->
                    <div class="lg:col-span-2">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
                            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
                                Método de Pago
                            </h2>

                            <!-- Selector de método de pago -->
                            <div class="space-y-3 mb-6">
                                <div
                                    v-for="metodo in metodosPago"
                                    :key="metodo.value"
                                    @click="metodoPagoSeleccionado = metodo.value"
                                    class="flex items-center gap-4 p-4 border-2 rounded-xl cursor-pointer transition-all"
                                    :class="metodoPagoSeleccionado === metodo.value 
                                        ? 'border-[#B3224D] bg-pink-50 dark:bg-pink-900/20' 
                                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'"
                                >
                                    <div class="flex-shrink-0">
                                        <div
                                            class="w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors"
                                            :class="metodoPagoSeleccionado === metodo.value 
                                                ? 'border-[#B3224D] bg-[#B3224D]' 
                                                : 'border-gray-300 dark:border-gray-600'"
                                        >
                                            <div
                                                v-if="metodoPagoSeleccionado === metodo.value"
                                                class="w-2 h-2 bg-white rounded-full"
                                            ></div>
                                        </div>
                                    </div>
                                    <component :is="metodo.icon" :size="24" class="text-gray-700 dark:text-gray-300" />
                                    <div class="flex-1">
                                        <p class="font-semibold text-gray-900 dark:text-white">
                                            {{ metodo.label }}
                                        </p>
                                        <p class="text-sm text-gray-600 dark:text-gray-400">
                                            {{ metodo.descripcion }}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <!-- Número de operación (opcional para transferencia) -->
                            <div v-if="metodoPagoSeleccionado === 'transferencia'" class="mb-6">
                                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                    Número de Operación (opcional)
                                </label>
                                <input
                                    v-model="nroOperacion"
                                    type="text"
                                    placeholder="Ej: 001234567890"
                                    class="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:border-[#B3224D] transition-colors"
                                />
                                <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                                    Ingresa el número de operación de tu transferencia bancaria
                                </p>
                            </div>

                            <!-- Botón de MercadoPago (solo si está seleccionado) -->
                            <div v-if="metodoPagoSeleccionado === 'mercadopago'" class="mb-6">
                                <div v-if="loadingMP" class="text-center py-8">
                                    <Loader2 :size="48" class="mx-auto mb-4 text-[#B3224D] animate-spin" />
                                    <p class="text-gray-600 dark:text-gray-400">
                                        Preparando pago seguro...
                                    </p>
                                </div>
                                <div v-else-if="errorMP" class="text-center py-6">
                                    <p class="text-red-600 dark:text-red-400 mb-4">{{ errorMP }}</p>
                                    <button
                                        @click="inicializarMercadoPago"
                                        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                    >
                                        Reintentar
                                    </button>
                                </div>
                                <div v-else>
                                    <!-- Contenedor del botón de MercadoPago -->
                                    <div id="mercadopago-button" class="min-h-[60px] mb-4"></div>
                                    <!-- Info de seguridad -->
                                    <div class="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-xl">
                                        <ShieldCheck :size="20" class="text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                                        <div class="text-sm text-green-800 dark:text-green-300">
                                            <p class="font-semibold mb-1">Pago 100% seguro</p>
                                            <p class="text-xs">Procesado por MercadoPago con encriptación SSL</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Nota informativa -->
                            <div v-if="metodoPagoSeleccionado !== 'mercadopago'" class="flex gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl mb-6">
                                <Info :size="20" class="text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                                <div class="text-sm text-blue-800 dark:text-blue-300">
                                    <p class="font-semibold mb-1">Información importante:</p>
                                    <p>Los datos del titular de cada ticket se completarán al momento de ingresar al evento mediante escaneo QR. Esto permite transferir o regalar tickets a otras personas.</p>
                                </div>
                            </div>

                            <!-- Botón de confirmar (solo para métodos tradicionales) -->
                            <button
                                v-if="metodoPagoSeleccionado !== 'mercadopago'"
                                @click="confirmarCompra"
                                :disabled="procesando"
                                class="w-full flex items-center justify-center gap-2 px-6 py-4 bg-[#B3224D] text-white rounded-xl font-bold text-lg hover:bg-[#8d1a3c] transition-colors shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Loader2 v-if="procesando" :size="20" class="animate-spin" />
                                <CreditCard v-else :size="20" />
                                {{ procesando ? 'Procesando...' : 'Confirmar Compra' }}
                            </button>
                        </div>
                    </div>

                    <!-- Resumen de compra -->
                    <div class="lg:col-span-1">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 sticky top-24">
                            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
                                Resumen
                            </h3>

                            <!-- Items -->
                            <div class="space-y-4 mb-6">
                                <div
                                    v-for="item in items"
                                    :key="`${item.eventoId}-${item.presentacionId}`"
                                    class="text-sm"
                                >
                                    <p class="font-semibold text-gray-900 dark:text-white mb-1">
                                        {{ item.eventoNombre }}
                                    </p>
                                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
                                        {{ formatearFecha(item.presentacionFecha) }} - {{ item.presentacionHora }}
                                    </p>
                                    <div class="pl-3 space-y-1">
                                        <div
                                            v-for="zona in item.zonas"
                                            :key="zona.id"
                                            class="flex justify-between text-xs text-gray-600 dark:text-gray-400"
                                        >
                                            <span>{{ zona.nombre }} (x{{ zona.cantidad }})</span>
                                            <span>S/ {{ (zona.precio * zona.cantidad).toFixed(2) }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
                                <div class="space-y-2 mb-4">
                                    <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                                        <span>Subtotal ({{ totalTickets }} tickets)</span>
                                        <span>S/ {{ subtotal.toFixed(2) }}</span>
                                    </div>
                                    <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                                        <span>Cargo por servicio (5%)</span>
                                        <span>S/ {{ cargoServicio.toFixed(2) }}</span>
                                    </div>
                                </div>
                                <div class="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-700">
                                    <span class="text-lg font-bold text-gray-900 dark:text-white">Total</span>
                                    <span class="text-2xl font-bold text-[#B3224D]">
                                        S/ {{ total.toFixed(2) }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Toast Notification -->
        <ToastNotification ref="toastRef" />
    </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppLayout from '@/Layouts/AppLayout.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import { useToasts } from '@/Helpers/useToasts';
import mercadopagoService from '@/services/mercadopagoService';
import {
    ArrowLeft,
    CreditCard,
    Banknote,
    Building2,
    Info,
    Loader2,
    Wallet,
    ShieldCheck
} from 'lucide-vue-next';
import {
    getCartItems,
    getCartTotal,
    clearCart
} from '@/Helpers/cartState';
import apiClient from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
const toastRef = ref(null);
const toast = useToasts(toastRef);

const items = ref([]);
const metodoPagoSeleccionado = ref('tarjeta');
const nroOperacion = ref('');
const procesando = ref(false);

// Estado de MercadoPago
const loadingMP = ref(false);
const errorMP = ref(null);
const mpInitialized = ref(false);

// Métodos de pago disponibles
const metodosPago = [
    {
        value: 'tarjeta',
        label: 'Tarjeta de Crédito/Débito',
        descripcion: 'Pago seguro con tarjeta',
        icon: CreditCard
    },
    {
        value: 'efectivo',
        label: 'Efectivo',
        descripcion: 'Pago en efectivo al recoger',
        icon: Banknote
    },
    {
        value: 'transferencia',
        label: 'Transferencia Bancaria',
        descripcion: 'Transferencia o depósito bancario',
        icon: Building2
    },
    {
        value: 'mercadopago',
        label: 'MercadoPago',
        descripcion: 'Pago seguro con MercadoPago',
        icon: Wallet
    }
];

// Cargar items del carrito
const loadItems = () => {
    items.value = getCartItems();
    
    // Verificar si el carrito está vacío
    if (items.value.length === 0) {
        toast.warning('Carrito vacío', 'No hay items en el carrito');
        router.push('/carrito');
    }
};

// Formatear fecha
const formatearFecha = (fecha) => {
    const date = new Date(fecha + 'T00:00:00');
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
};

// Cálculos
const totalTickets = computed(() => {
    return items.value.reduce((total, item) => {
        return total + item.zonas.reduce((sum, zona) => sum + zona.cantidad, 0);
    }, 0);
});

const subtotal = computed(() => {
    return getCartTotal();
});

const cargoServicio = computed(() => {
    return subtotal.value * 0.05;
});

const total = computed(() => {
    return subtotal.value + cargoServicio.value;
});

// Inicializar MercadoPago
const inicializarMercadoPago = async () => {
    loadingMP.value = true;
    errorMP.value = null;

    try {
        // Paso 1: Sincronizar carrito del localStorage con el backend
        const carritoResponse = await mercadopagoService.sincronizarCarrito(items.value);
        
        if (!carritoResponse.success) {
            throw new Error(carritoResponse.error || 'Error al sincronizar el carrito');
        }

        const carritoId = carritoResponse.carrito.id;

        // Paso 2: Crear preferencia de pago usando el carrito_id
        const preferenciaResponse = await mercadopagoService.crearPreferencia(carritoId);

        if (!preferenciaResponse.preference_id) {
            throw new Error('No se pudo crear la preferencia de pago');
        }

        const preferenceId = preferenciaResponse.preference_id;
        
        // Paso 3: Inicializar SDK de MercadoPago
        const publicKey = import.meta.env.VITE_MERCADOPAGO_PUBLIC_KEY;
        
        if (!publicKey) {
            throw new Error('Clave pública de MercadoPago no configurada');
        }

        const mp = mercadopagoService.inicializarSDK(publicKey);
        
        if (!mp) {
            throw new Error('No se pudo inicializar el SDK de MercadoPago');
        }
        
        // Paso 4: Renderizar botón de pago
        mercadopagoService.renderizarBotonPago(mp, preferenceId, 'mercadopago-button');
        
        mpInitialized.value = true;
        
    } catch (error) {
        console.error('Error al inicializar MercadoPago:', error);
        errorMP.value = error.response?.data?.error || error.message || 'Error al conectar con MercadoPago';
    } finally {
        loadingMP.value = false;
    }
};

// Watch para inicializar MP cuando se selecciona
watch(metodoPagoSeleccionado, (nuevoMetodo) => {
    if (nuevoMetodo === 'mercadopago' && !mpInitialized.value) {
        inicializarMercadoPago();
    }
});

// Confirmar compra
const confirmarCompra = async () => {
    if (procesando.value) return;

    // Verificar autenticación
    if (!authStore.isAuthenticated) {
        toast.warning('Sesión expirada', 'Por favor, inicia sesión nuevamente');
        sessionStorage.setItem('redirectAfterLogin', '/checkout');
        router.push('/login');
        return;
    }

    // Preparar datos para el checkout
    const checkoutData = {
        metodo_pago: metodoPagoSeleccionado.value,
        nro_operacion: metodoPagoSeleccionado.value === 'transferencia' ? nroOperacion.value : null,
        items: items.value.flatMap(item => 
            item.zonas.map(zona => ({
                presentacion_id: item.presentacionId,
                zona_id: zona.id,
                cantidad: zona.cantidad
            }))
        )
    };

    try {
        procesando.value = true;
        
        const response = await apiClient.post('/ventas/checkout/', checkoutData);
        
        if (response.data.success) {
            // Limpiar carrito
            clearCart();
            
            // Mostrar mensaje de éxito
            toast.success('¡Compra exitosa!', 'Tu compra se ha procesado correctamente');
            
            // Redirigir a una página de confirmación o mis tickets
            setTimeout(() => {
                router.push('/mis-tickets');
            }, 1500);
        } else {
            toast.error('Error', response.data.error || 'No se pudo procesar la compra');
        }
    } catch (error) {
        console.error('Error en checkout:', error);
        
        let mensaje = 'Ocurrió un error al procesar tu compra';
        
        if (error.response?.data?.details) {
            // Mostrar detalles del error
            const details = error.response.data.details;
            if (typeof details === 'string') {
                mensaje = details;
            } else if (typeof details === 'object') {
                mensaje = Object.values(details).flat().join(', ');
            }
        } else if (error.response?.data?.error) {
            mensaje = error.response.data.error;
        }
        
        toast.error('Error en el checkout', mensaje);
    } finally {
        procesando.value = false;
    }
};

onMounted(() => {
    // Verificar autenticación
    if (!authStore.isAuthenticated) {
        toast.warning('Inicia sesión', 'Debes iniciar sesión para continuar');
        sessionStorage.setItem('redirectAfterLogin', '/checkout');
        router.push('/login');
        return;
    }
    
    loadItems();
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
