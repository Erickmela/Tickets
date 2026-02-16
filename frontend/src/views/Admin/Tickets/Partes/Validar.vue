<script setup>
import { ref, computed, onUnmounted } from 'vue';
import AdmLayout from '@/Layouts/AdmLayout.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import { Search, User, QrCode, MapPin, Calendar, Hash, AlertCircle, Loader2, CheckCircle, XCircle, Clock, Ticket, CreditCard, DollarSign, ChevronLeft, ChevronRight } from 'lucide-vue-next';
import { ventasService } from '@/services/ventasService';
import { useToasts } from '@/Helpers/useToasts';

const toast = ref(null);
const toastHelper = useToasts(toast);

const dniBusqueda = ref('');
const buscando = ref(false);
const ticketsEncontrados = ref([]);
const ticketSeleccionado = ref(null);
const errorBusqueda = ref('');
const countdown = ref(0);

// Paginación
const paginaActual = ref(1);
const ticketsPorPagina = 5;

let countdownInterval = null;

const ticketsPaginados = computed(() => {
    const inicio = (paginaActual.value - 1) * ticketsPorPagina;
    const fin = inicio + ticketsPorPagina;
    return ticketsEncontrados.value.slice(inicio, fin);
});

const totalPaginas = computed(() => {
    return Math.ceil(ticketsEncontrados.value.length / ticketsPorPagina);
});

const buscarTickets = async () => {
    if (buscando.value || countdown.value > 0) return;

    if (!dniBusqueda.value || dniBusqueda.value.length < 8) {
        mostrarError('Ingrese un DNI válido (mínimo 8 dígitos)');
        return;
    }

    buscando.value = true;
    errorBusqueda.value = '';
    ticketSeleccionado.value = null;
    ticketsEncontrados.value = [];
    paginaActual.value = 1;

    try {
        const resultados = await ventasService.buscarTicketsPorDNI(dniBusqueda.value);

        if (!resultados || resultados.length === 0) {
            mostrarError('No se encontraron tickets con este DNI');
        } else {
            // Ordenar del más reciente al más antiguo
            ticketsEncontrados.value = resultados.sort((a, b) =>
                new Date(b.fecha_creacion) - new Date(a.fecha_creacion)
            );
            toastHelper.success('Búsqueda exitosa', `Se encontraron ${resultados.length} ticket(s)`);
        }
    } catch (error) {
        console.error('Error al buscar tickets:', error);
        mostrarError(error.response?.data?.error || 'Error al buscar tickets');
    } finally {
        buscando.value = false;
    }
};

const cargarTicket = async (ticketId) => {
    try {
        const ticketCompleto = await ventasService.getTicket(ticketId);
        ticketSeleccionado.value = ticketCompleto;
    } catch (error) {
        console.error('Error al cargar ticket:', error);
        mostrarError('Error al cargar los detalles del ticket');
    }
};

const seleccionarTicket = async (ticket) => {
    await cargarTicket(ticket.id);
};

const volverAListaTickets = () => {
    ticketSeleccionado.value = null;
};

const mostrarError = (mensaje) => {
    ticketSeleccionado.value = null;
    ticketsEncontrados.value = [];
    errorBusqueda.value = mensaje;
    iniciarCuentaRegresiva(10);
};

const iniciarCuentaRegresiva = (segundos) => {
    countdown.value = segundos;
    if (countdownInterval) clearInterval(countdownInterval);
    countdownInterval = setInterval(() => {
        if (countdown.value > 0) {
            countdown.value--;
        } else {
            errorBusqueda.value = '';
            clearInterval(countdownInterval);
            countdownInterval = null;
        }
    }, 1000);
};

const volverABuscar = () => {
    dniBusqueda.value = '';
    ticketSeleccionado.value = null;
    ticketsEncontrados.value = [];
    errorBusqueda.value = '';
    paginaActual.value = 1;
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    countdown.value = 0;
};

const cambiarPagina = (pagina) => {
    if (pagina >= 1 && pagina <= totalPaginas.value) {
        paginaActual.value = pagina;
    }
};

const getEstadoBadgeClass = (estado) => {
    const classes = {
        ACTIVO: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        USADO: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        ANULADO: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
    };
    return classes[estado] || 'bg-gray-100 text-gray-800';
};

const getEstadoIcon = (estado) => {
    return estado === 'ACTIVO' ? CheckCircle : estado === 'USADO' ? Clock : XCircle;
};

const qrImageUrl = computed(() => {
    if (ticketSeleccionado.value?.qr_image_url) {
        return ticketSeleccionado.value.qr_image_url;
    }

    if (ticketSeleccionado.value?.qr_image) {
        const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';
        return `${baseUrl}/media/${ticketSeleccionado.value.qr_image}`;
    }

    return null;
});

const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

onUnmounted(() => {
    if (countdownInterval) clearInterval(countdownInterval);
});
</script>

<template>
    <AdmLayout>
        <ToastNotification ref="toast" />

        <div class="py-6">
            <!-- Vista de Búsqueda -->
            <div v-if="ticketsEncontrados.length === 0 && !ticketSeleccionado" class="w-full max-w-4xl mx-auto">
                <!-- Logo / Isotipo -->
                <div class="text-center mb-8">
                    <div
                        class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-[#B3224D] to-[#8B1A3D] mb-4 shadow-lg">
                        <QrCode class="h-10 w-10 text-white" stroke-width="2.5" />
                    </div>
                    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                        Validador de Tickets
                    </h1>
                    <p class="text-gray-600 dark:text-gray-400">
                        Ingresa el DNI del titular para validar su ticket
                    </p>
                </div>

                <!-- Card de búsqueda -->
                <div
                    class="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
                    <div class="p-8">
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                    DNI del Titular
                                </label>
                                <div class="relative">
                                    <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                        <User class="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input v-model="dniBusqueda" type="text" placeholder="Ingrese el DNI" maxlength="8"
                                        class="w-full pl-12 pr-4 py-3.5 text-lg border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-[#B3224D] focus:border-[#B3224D] dark:bg-gray-700 dark:text-white transition-all"
                                        @keyup.enter="buscarTickets" :disabled="buscando || countdown > 0" />
                                </div>
                            </div>

                            <button @click="buscarTickets"
                                :disabled="buscando || !dniBusqueda || dniBusqueda.length < 8 || countdown > 0"
                                class="w-full py-3.5 bg-gradient-to-r from-[#B3224D] to-[#8B1A3D] text-white text-lg font-semibold rounded-xl hover:shadow-lg hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2">
                                <Loader2 v-if="buscando" class="h-5 w-5 animate-spin" />
                                <Search v-else class="h-5 w-5" />
                                <span>{{ buscando ? 'Buscando...' : 'Buscar Ticket' }}</span>
                            </button>
                        </div>

                        <!-- Error de búsqueda -->
                        <div v-if="errorBusqueda"
                            class="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl">
                            <div class="flex items-start gap-3">
                                <AlertCircle class="h-6 w-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                                <div class="flex-1">
                                    <p class="text-red-700 dark:text-red-300 font-semibold mb-1">
                                        {{ errorBusqueda }}
                                    </p>
                                    <p v-if="countdown > 0" class="text-sm text-red-600 dark:text-red-400">
                                        Podrás buscar nuevamente en {{ countdown }} segundo{{ countdown !== 1 ? 's' : ''
                                        }}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Vista de Lista de Tickets -->
            <div v-else-if="ticketsEncontrados.length > 0 && !ticketSeleccionado" class="w-full max-w-5xl mx-auto">
                <!-- Header -->
                <div class="mb-6 flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                            Tickets Encontrados
                        </h2>
                        <p class="text-gray-600 dark:text-gray-400">
                            {{ ticketsEncontrados.length }} ticket(s) para DNI: {{ dniBusqueda }}
                        </p>
                    </div>
                    <button @click="volverABuscar"
                        class="px-5 py-2.5 bg-gradient-to-r from-[#B3224D] to-[#8B1A3D] text-white rounded-xl hover:shadow-lg hover:scale-[1.02] transition-all flex items-center gap-2 font-semibold">
                        <Search class="h-5 w-5" />
                        <span>Nueva Búsqueda</span>
                    </button>
                </div>

                <!-- Lista de tickets -->
                <div class="space-y-4">
                    <div v-for="ticket in ticketsPaginados" :key="ticket.id" @click="seleccionarTicket(ticket)"
                        class="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-xl hover:scale-[1.01] transition-all cursor-pointer">
                        <div class="flex items-center justify-between gap-4 flex-wrap">
                            <div class="flex items-center gap-4 flex-1">
                                <div class="p-3 bg-[#B3224D]/10 rounded-xl">
                                    <Ticket class="h-8 w-8 text-[#B3224D]" />
                                </div>
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center gap-3 mb-2">
                                        <h3 class="text-lg font-bold text-gray-900 dark:text-white truncate">
                                            {{ ticket.evento_nombre || 'Evento' }}
                                        </h3>
                                        <span class="px-3 py-1 rounded-lg text-xs font-bold whitespace-nowrap"
                                            :class="getEstadoBadgeClass(ticket.estado)">
                                            {{ ticket.estado }}
                                        </span>
                                    </div>
                                    <div
                                        class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm text-gray-600 dark:text-gray-400">
                                        <div class="flex items-center gap-2">
                                            <MapPin class="h-4 w-4 flex-shrink-0" />
                                            <span class="truncate">{{ ticket.zona?.nombre || 'Zona' }}</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <Calendar class="h-4 w-4 flex-shrink-0" />
                                            <span>{{ new Date(ticket.fecha_creacion).toLocaleDateString('es-PE')
                                                }}</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <Hash class="h-4 w-4 flex-shrink-0" />
                                            <span class="truncate font-mono text-xs">{{ ticket.codigo_uuid.substring(0,
                                                8) }}...</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                <div class="text-right">
                                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Precio</p>
                                    <p class="text-xl font-bold text-[#B3224D] dark:text-[#e02855]">
                                        S/ {{ ticket.zona?.precio || '0.00' }}
                                    </p>
                                </div>
                                <ChevronRight class="h-6 w-6 text-gray-400" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Paginación -->
                <div v-if="totalPaginas > 1" class="mt-6 flex items-center justify-center gap-2">
                    <button @click="cambiarPagina(paginaActual - 1)" :disabled="paginaActual === 1"
                        class="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                        <ChevronLeft class="h-5 w-5 text-gray-600 dark:text-gray-400" />
                    </button>

                    <div class="flex gap-1">
                        <button v-for="pagina in totalPaginas" :key="pagina" @click="cambiarPagina(pagina)"
                            class="px-4 py-2 rounded-lg font-semibold transition-colors"
                            :class="pagina === paginaActual
                                ? 'bg-gradient-to-r from-[#B3224D] to-[#8B1A3D] text-white'
                                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'">
                            {{ pagina }}
                        </button>
                    </div>

                    <button @click="cambiarPagina(paginaActual + 1)" :disabled="paginaActual === totalPaginas"
                        class="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                        <ChevronRight class="h-5 w-5 text-gray-600 dark:text-gray-400" />
                    </button>
                </div>
            </div>

            <!-- Vista de Detalle del Ticket -->
            <div v-else-if="ticketSeleccionado" class="w-full">
                <!-- Botón volver -->
                <div class="mb-6 flex gap-3">
                    <button @click="volverAListaTickets"
                        class="px-6 py-3 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl hover:shadow-lg transition-all flex items-center gap-2 font-semibold border border-gray-300 dark:border-gray-600">
                        <ChevronLeft class="h-5 w-5" />
                        <span>Volver a la lista</span>
                    </button>
                    <button @click="volverABuscar"
                        class="px-6 py-3 bg-gradient-to-r from-[#B3224D] to-[#8B1A3D] text-white rounded-xl hover:shadow-lg hover:scale-[1.02] transition-all flex items-center gap-2 font-semibold">
                        <Search class="h-5 w-5" />
                        <span>Nueva Búsqueda</span>
                    </button>
                </div>

                <!-- Card principal -->
                <div
                    class="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
                    <!-- Header -->
                    <div class="bg-gradient-to-r from-[#B3224D] to-[#8B1A3D] p-6">
                        <div class="flex items-center justify-between flex-wrap gap-4">
                            <div class="flex items-center gap-3">
                                <component :is="getEstadoIcon(ticketSeleccionado.estado)" class="h-8 w-8 text-white" />
                                <div>
                                    <h2 class="text-2xl font-bold text-white">
                                        {{ ticketSeleccionado.evento_nombre || ticketSeleccionado.zona?.evento_nombre ||
                                        'Evento' }}
                                    </h2>
                                    <p class="text-white/80 text-sm mt-0.5">
                                        Ticket validado correctamente
                                    </p>
                                </div>
                            </div>
                            <span class="px-4 py-2 rounded-xl text-sm font-bold shadow-lg"
                                :class="getEstadoBadgeClass(ticketSeleccionado.estado)">
                                {{ ticketSeleccionado.estado }}
                            </span>
                        </div>
                    </div>

                    <!-- Contenido principal -->
                    <div class="p-6 md:p-8">
                        <div class="grid grid-cols-1 lg:grid-cols-10 gap-6">
                            <!-- Sección principal - 7 columnas -->
                            <section class="lg:col-span-7">
                                <h2 class="text-xl font-bold text-gray-800 dark:text-gray-300 mb-6">
                                    Detalles del Ticket
                                </h2>

                                <div class="border-t border-gray-300 dark:border-gray-700 pt-6">
                                    <!-- Grid de información - 2 columnas -->
                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 text-gray-800 dark:text-white">
                                        <!-- Nombre del titular -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Nombre del titular
                                            </p>
                                            <p class="text-lg font-semibold">
                                                {{ ticketSeleccionado.nombre_titular }}
                                            </p>
                                        </div>

                                        <!-- DNI del titular -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                DNI del titular
                                            </p>
                                            <p class="text-lg font-semibold font-mono">
                                                {{ ticketSeleccionado.dni_titular }}
                                            </p>
                                        </div>

                                        <!-- Evento -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Evento
                                            </p>
                                            <p class="text-lg font-semibold">
                                                {{ ticketSeleccionado.evento_nombre ||
                                                ticketSeleccionado.zona?.evento_nombre || '-' }}
                                            </p>
                                        </div>

                                        <!-- Fecha del evento -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Fecha del evento
                                            </p>
                                            <p class="text-lg font-semibold">
                                                {{ ticketSeleccionado.zona?.evento_fecha ? new
                                                    Date(ticketSeleccionado.zona.evento_fecha).toLocaleDateString('es-PE', {
                                                year: 'numeric', month: 'long', day: 'numeric' }) : '-' }}
                                            </p>
                                        </div>

                                        <!-- Lugar -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Lugar del evento
                                            </p>
                                            <p class="text-lg font-semibold">
                                                {{ ticketSeleccionado.zona?.evento_lugar || '-' }}
                                            </p>
                                        </div>

                                        <!-- Zona -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Zona
                                            </p>
                                            <p class="text-lg font-semibold">
                                                {{ ticketSeleccionado.zona?.nombre || '-' }}
                                            </p>
                                        </div>

                                        <!-- Precio -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Precio
                                            </p>
                                            <p class="text-2xl font-bold text-[#B3224D] dark:text-[#e02855]">
                                                S/ {{ ticketSeleccionado.zona?.precio || '0.00' }}
                                            </p>
                                        </div>

                                        <!-- Fecha de emisión -->
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Fecha de emisión
                                            </p>
                                            <p class="text-lg font-semibold">
                                                {{ formatFecha(ticketSeleccionado.fecha_creacion) }}
                                            </p>
                                        </div>

                                        <!-- Código único - span completo -->
                                        <div class="sm:col-span-2">
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                                                Código único del ticket
                                            </p>
                                            <p
                                                class="text-base font-mono text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 p-3 rounded-lg break-all">
                                                {{ ticketSeleccionado.codigo_uuid }}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Nota informativa -->
                                <div
                                    class="mt-8 border-t border-gray-300 dark:border-gray-700 pt-6 text-gray-500 dark:text-gray-400 text-sm leading-relaxed">
                                    <p>
                                        Este ticket es válido para el ingreso al evento especificado. Debe presentarse
                                        junto con un documento de identidad que coincida con el DNI del titular
                                        registrado.
                                    </p>
                                </div>
                            </section>

                            <!-- Aside - Código QR (3 columnas) -->
                            <aside class="lg:col-span-3 bg-gray-100 dark:bg-gray-900 rounded-xl flex flex-col p-6">
                                <div class="text-center mb-6">
                                    <QrCode class="h-10 w-10 text-[#B3224D] mx-auto mb-3" />
                                    <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1">
                                        Código QR
                                    </h3>
                                    <p class="text-sm text-gray-600 dark:text-gray-400">
                                        Escanea este código para validar el ticket
                                    </p>
                                </div>

                                <!-- QR Image -->
                                <div class="flex justify-center mb-6">
                                    <div v-if="qrImageUrl" class="bg-white p-4 rounded-xl shadow-lg">
                                        <img :src="qrImageUrl" :alt="`QR Ticket ${ticketSeleccionado.id}`"
                                            class="w-full max-w-xs h-auto object-contain" />
                                    </div>
                                    <div v-else
                                        class="w-full max-w-xs aspect-square flex items-center justify-center bg-gray-200 dark:bg-gray-600 rounded-xl">
                                        <div class="text-center p-4">
                                            <AlertCircle class="w-12 h-12 text-gray-400 mx-auto mb-2" />
                                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                                QR no disponible
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Estado del ticket -->
                                <div class="mt-auto">
                                    <div v-if="ticketSeleccionado.estado === 'ACTIVO'"
                                        class="p-4 bg-green-100 dark:bg-green-900/30 border-2 border-green-300 dark:border-green-700 rounded-xl">
                                        <div class="flex items-center gap-3 justify-center">
                                            <CheckCircle class="h-6 w-6 text-green-700 dark:text-green-400" />
                                            <div class="text-center">
                                                <p class="text-base text-green-800 dark:text-green-300 font-bold">
                                                    Ticket Válido
                                                </p>
                                                <p class="text-xs text-green-700 dark:text-green-400">
                                                    Listo para usar
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <div v-if="ticketSeleccionado.estado === 'USADO'"
                                        class="p-4 bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-300 dark:border-blue-700 rounded-xl">
                                        <div class="flex items-center gap-3 justify-center">
                                            <Clock class="h-6 w-6 text-blue-700 dark:text-blue-400" />
                                            <div class="text-center">
                                                <p class="text-base text-blue-800 dark:text-blue-300 font-bold">
                                                    Ticket Usado
                                                </p>
                                                <p class="text-xs text-blue-700 dark:text-blue-400">
                                                    Ya fue utilizado
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <div v-if="ticketSeleccionado.estado === 'ANULADO'"
                                        class="p-4 bg-red-100 dark:bg-red-900/30 border-2 border-red-300 dark:border-red-700 rounded-xl">
                                        <div class="flex items-center gap-3 justify-center">
                                            <XCircle class="h-6 w-6 text-red-700 dark:text-red-400" />
                                            <div class="text-center">
                                                <p class="text-base text-red-800 dark:text-red-300 font-bold">
                                                    Ticket Anulado
                                                </p>
                                                <p class="text-xs text-red-700 dark:text-red-400">
                                                    No válido para ingreso
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </aside>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AdmLayout>
</template>
