<template>
    <AppLayout title="Carrito de Compras">
        <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
            <div class="container mx-auto px-4">
                <!-- Header -->
                <div class="mb-8">
                    <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
                        🛒 Mi Carrito
                    </h1>
                    <p class="text-gray-600 dark:text-gray-400">
                        Revisa tus tickets antes de finalizar la compra
                    </p>
                </div>

                <!-- Carrito vacío -->
                <div v-if="items.length === 0" class="text-center py-16">
                    <ShoppingCart :size="80" :stroke-width="1.5" class="mx-auto mb-6 text-gray-400" />
                    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                        Tu carrito está vacío
                    </h2>
                    <p class="text-gray-600 dark:text-gray-400 mb-8">
                        ¡Agrega algunos eventos increíbles a tu carrito!
                    </p>
                    <RouterLink
                        to="/eventos"
                        class="inline-flex items-center gap-2 px-6 py-3 bg-[#B3224D] text-white rounded-xl font-semibold hover:bg-[#8d1a3c] transition-colors"
                    >
                        <Sparkles :size="20" />
                        Explorar Eventos
                    </RouterLink>
                </div>

                <!-- Items del carrito -->
                <div v-else class="grid lg:grid-cols-3 gap-8">
                    <!-- Lista de items -->
                    <div class="lg:col-span-2 space-y-4">
                        <div
                            v-for="item in items"
                            :key="`${item.eventoId}-${item.presentacionId}`"
                            class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden"
                        >
                            <div class="flex flex-col md:flex-row gap-4 p-6">
                                <!-- Imagen del evento -->
                                <div class="flex-shrink-0">
                                    <img
                                        v-if="item.eventoImagen"
                                        :src="item.eventoImagen"
                                        :alt="item.eventoNombre"
                                        class="w-full md:w-32 h-48 md:h-32 object-cover rounded-xl"
                                    />
                                    <div
                                        v-else
                                        class="w-full md:w-32 h-48 md:h-32 bg-gradient-to-br from-[#B3224D] to-[#8d1a3c] rounded-xl flex items-center justify-center"
                                    >
                                        <Calendar :size="40" class="text-white" />
                                    </div>
                                </div>

                                <!-- Información del evento -->
                                <div class="flex-1">
                                    <div class="flex justify-between items-start mb-3">
                                        <div>
                                            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1">
                                                {{ item.eventoNombre }}
                                            </h3>
                                            <div class="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400">
                                                <span class="flex items-center gap-1">
                                                    <Calendar :size="16" />
                                                    {{ formatearFecha(item.presentacionFecha) }}
                                                </span>
                                                <span class="flex items-center gap-1">
                                                    <Clock :size="16" />
                                                    {{ item.presentacionHora }}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            @click="eliminarItem(item.eventoId, item.presentacionId)"
                                            class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                                            title="Eliminar del carrito"
                                        >
                                            <Trash2 :size="20" />
                                        </button>
                                    </div>

                                    <!-- Zonas -->
                                    <div class="space-y-2">
                                        <div
                                            v-for="zona in item.zonas"
                                            :key="zona.id"
                                            class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                                        >
                                            <div class="flex-1">
                                                <p class="font-semibold text-gray-900 dark:text-white">
                                                    {{ zona.nombre }}
                                                </p>
                                                <p class="text-sm text-gray-600 dark:text-gray-400">
                                                    S/ {{ zona.precio.toFixed(2) }} c/u
                                                </p>
                                            </div>

                                            <!-- Controles de cantidad -->
                                            <div class="flex items-center gap-3">
                                                <button
                                                    @click="disminuirCantidad(item.eventoId, item.presentacionId, zona.id, zona.cantidad)"
                                                    class="w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 font-bold transition-colors"
                                                >
                                                    -
                                                </button>
                                                <span class="w-8 text-center font-bold text-gray-900 dark:text-white">
                                                    {{ zona.cantidad }}
                                                </span>
                                                <button
                                                    @click="aumentarCantidad(item.eventoId, item.presentacionId, zona.id, zona.cantidad)"
                                                    class="w-8 h-8 rounded-lg bg-[#B3224D] hover:bg-[#8d1a3c] text-white font-bold transition-colors"
                                                >
                                                    +
                                                </button>
                                            </div>

                                            <div class="ml-4 text-right">
                                                <p class="font-bold text-gray-900 dark:text-white">
                                                    S/ {{ (zona.precio * zona.cantidad).toFixed(2) }}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Botón volver -->
                        <RouterLink
                            to="/eventos"
                            class="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-[#B3224D] transition-colors"
                        >
                            <ArrowLeft :size="20" />
                            Seguir comprando
                        </RouterLink>
                    </div>

                    <!-- Resumen de compra -->
                    <div class="lg:col-span-1">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 sticky top-24">
                            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
                                Resumen de Compra
                            </h3>

                            <!-- Desglose -->
                            <div class="space-y-3 mb-6">
                                <div class="flex justify-between text-gray-600 dark:text-gray-400">
                                    <span>Tickets ({{ totalTickets }})</span>
                                    <span>S/ {{ subtotal.toFixed(2) }}</span>
                                </div>
                                <div class="flex justify-between text-gray-600 dark:text-gray-400">
                                    <span>Cargo por servicio</span>
                                    <span>S/ {{ cargoServicio.toFixed(2) }}</span>
                                </div>
                            </div>

                            <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mb-6">
                                <div class="flex justify-between items-center">
                                    <span class="text-lg font-semibold text-gray-900 dark:text-white">Total</span>
                                    <span class="text-2xl font-bold text-[#B3224D]">
                                        S/ {{ total.toFixed(2) }}
                                    </span>
                                </div>
                            </div>

                            <!-- Botones de acción -->
                            <button
                                @click="procederCompra"
                                class="w-full flex items-center justify-center gap-2 px-6 py-4 bg-[#B3224D] text-white rounded-xl font-bold text-lg hover:bg-[#8d1a3c] transition-colors shadow-lg hover:shadow-xl mb-3"
                            >
                                <CreditCard :size="20" />
                                Proceder al Pago
                            </button>

                            <button
                                @click="limpiarCarrito"
                                class="w-full px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                            >
                                Vaciar Carrito
                            </button>
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
import { ref, computed, onMounted } from 'vue';
import { useRouter, RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppLayout from '@/Layouts/AppLayout.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import { useToasts } from '@/Helpers/useToasts';
import {
    ShoppingCart,
    Calendar,
    Clock,
    Trash2,
    ArrowLeft,
    CreditCard,
    Info,
    Sparkles
} from 'lucide-vue-next';
import {
    getCartItems,
    removeFromCart,
    updateZonaCantidad,
    clearCart,
    getCartTotal
} from '@/Helpers/cartState';

const router = useRouter();
const authStore = useAuthStore();
const toastRef = ref(null);
const toast = useToasts(toastRef);

const items = ref([]);

// Cargar items del carrito
const loadItems = () => {
    items.value = getCartItems();
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

// Eliminar item completo
const eliminarItem = (eventoId, presentacionId) => {
    removeFromCart(eventoId, presentacionId);
    loadItems();
    toast.success('Item eliminado', 'Se eliminó el item del carrito');
};

// Aumentar cantidad
const aumentarCantidad = (eventoId, presentacionId, zonaId, cantidadActual) => {
    updateZonaCantidad(eventoId, presentacionId, zonaId, cantidadActual + 1);
    loadItems();
};

// Disminuir cantidad
const disminuirCantidad = (eventoId, presentacionId, zonaId, cantidadActual) => {
    if (cantidadActual > 1) {
        updateZonaCantidad(eventoId, presentacionId, zonaId, cantidadActual - 1);
        loadItems();
    } else {
        // Si la cantidad es 1, preguntar si desea eliminar
        updateZonaCantidad(eventoId, presentacionId, zonaId, 0);
        loadItems();
        toast.info('Zona eliminada', 'Se eliminó la zona del carrito');
    }
};

// Limpiar carrito
const limpiarCarrito = () => {
    if (confirm('¿Estás seguro de que deseas vaciar el carrito?')) {
        clearCart();
        loadItems();
        toast.success('Carrito vaciado', 'Se eliminaron todos los items');
    }
};

// Proceder a la compra
const procederCompra = () => {
    // Verificar si el usuario está autenticado
    if (!authStore.isAuthenticated) {
        toast.warning('Inicia sesión', 'Debes iniciar sesión para continuar con la compra');
        // Guardar que debe ir al checkout después del login
        sessionStorage.setItem('redirectAfterLogin', '/checkout');
        // Redirigir a login
        setTimeout(() => {
            router.push('/login');
        }, 500);
        return;
    }

    // Si está autenticado, redirigir al checkout
    router.push('/checkout');
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
    // 5% de cargo por servicio
    return subtotal.value * 0.05;
});

const total = computed(() => {
    return subtotal.value + cargoServicio.value;
});

onMounted(() => {
    loadItems();
});
</script>

<style scoped>
/* Animaciones suaves */
.transition-all {
    transition: all 0.3s ease;
}
</style>
