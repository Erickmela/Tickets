<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import AppLayout from '@/Layouts/AppLayout.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import { useToasts } from '@/Helpers/useToasts';
import {
    Calendar,
    MapPin,
    Tag,
    Clock,
    FileText,
    Info,
    Users,
    ShoppingCart,
    ArrowLeft,
    AlertCircle,
    Music,
    Trophy,
    Drama,
    Mic,
    Tent,
    Utensils,
    PartyPopper,
    Sparkles,
    ImageIcon as ImageIcon
} from 'lucide-vue-next';
import { eventosService } from '@/services/eventosService';
import { addToCart } from '@/Helpers/cartState';

const route = useRoute();
const evento = ref(null);
const loading = ref(true);
const error = ref(null);
const presentacionSeleccionada = ref(null);
const cantidadesZonas = ref({});
const toastRef = ref(null);

const toast = useToasts(toastRef);

// Mapeo de categorías a iconos
const categoriaIconos = {
    'Música': Music,
    'Musica': Music,
    'Deportes': Trophy,
    'Teatro': Drama,
    'Conferencias': Mic,
    'Festivales': Tent,
    'Gastronomía': Utensils,
    'Gastronomia': Utensils,
    'Infantiles': PartyPopper,
    'Otros': Sparkles
};

// Obtener el icono de la categoría
const iconoCategoria = computed(() => {
    return categoriaIconos[evento.value?.categoria] || Sparkles;
});

// Imagen principal
const imagenPrincipal = computed(() => {
    if (evento.value?.imagen_principal) {
        if (evento.value.imagen_principal.startsWith('http')) {
            return evento.value.imagen_principal;
        }
        // Eliminar /api del final si existe, ya que media se sirve desde la raíz
        const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/api$/, '');
        return `${baseUrl}${evento.value.imagen_principal}`;
    }
    return null;
});

// Galería de imágenes
const galeria = computed(() => {
    const imagenes = [];
    // Eliminar /api del final si existe, ya que media se sirve desde la raíz
    const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/api$/, '');

    if (evento.value?.imagen_banner && evento.value.imagen_banner !== evento.value.imagen_principal) {
        const url = evento.value.imagen_banner.startsWith('http')
            ? evento.value.imagen_banner
            : `${baseUrl}${evento.value.imagen_banner}`;
        imagenes.push(url);
    }
    if (evento.value?.imagen_flyer && evento.value.imagen_flyer !== evento.value.imagen_principal) {
        const url = evento.value.imagen_flyer.startsWith('http')
            ? evento.value.imagen_flyer
            : `${baseUrl}${evento.value.imagen_flyer}`;
        imagenes.push(url);
    }
    if (evento.value?.imagen_cartel && evento.value.imagen_cartel !== evento.value.imagen_principal) {
        const url = evento.value.imagen_cartel.startsWith('http')
            ? evento.value.imagen_cartel
            : `${baseUrl}${evento.value.imagen_cartel}`;
        imagenes.push(url);
    }
    if (evento.value?.imagen_mapa) {
        const url = evento.value.imagen_mapa.startsWith('http')
            ? evento.value.imagen_mapa
            : `${baseUrl}${evento.value.imagen_mapa}`;
        imagenes.push(url);
    }

    return imagenes;
});

// Formatear fecha
const fechaFormateada = computed(() => {
    if (!evento.value?.fecha) return '';
    const fecha = new Date(evento.value.fecha);
    return fecha.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
});

// Precio mínimo
const precioMinimo = computed(() => {
    if (evento.value?.presentaciones && evento.value.presentaciones.length > 0) {
        const precios = [];
        evento.value.presentaciones.forEach(presentacion => {
            if (presentacion.zonas && presentacion.zonas.length > 0) {
                presentacion.zonas.forEach(zona => {
                    precios.push(parseFloat(zona.precio));
                });
            }
        });
        if (precios.length > 0) {
            const precioMin = Math.min(...precios);
            return `S/ ${precioMin.toFixed(2)}`;
        }
    }
    return 'Consultar';
});

// Formatear fecha de presentación
const formatearFecha = (fecha) => {
    if (!fecha) return '';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
        weekday: 'long',
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
};

// Formatear día y mes para cards
const formatearDiaMes = (fecha) => {
    if (!fecha) return { dia: '', mes: '' };
    const date = new Date(fecha + 'T00:00:00');
    const dia = date.getDate().toString().padStart(2, '0');
    const mes = date.toLocaleDateString('es-ES', { month: 'short' }).toUpperCase().replace('.', '');
    return { dia, mes };
};

// Zonas disponibles de la presentación seleccionada
const zonasDisponibles = computed(() => {
    if (!presentacionSeleccionada.value || !presentacionSeleccionada.value.zonas) {
        return [];
    }
    return presentacionSeleccionada.value.zonas.filter(z => z.activo !== false);
});

// Precio total basado en las cantidades seleccionadas
const precioTotal = computed(() => {
    let total = 0;
    for (const [zonaId, cantidad] of Object.entries(cantidadesZonas.value)) {
        if (cantidad > 0) {
            const zona = zonasDisponibles.value.find(z => z.id == zonaId);
            if (zona) {
                total += parseFloat(zona.precio) * cantidad;
            }
        }
    }
    return total;
});

// Seleccionar presentación
const seleccionarPresentacion = (presentacion) => {
    presentacionSeleccionada.value = presentacion;
    // Resetear cantidades al cambiar de presentación
    cantidadesZonas.value = {};
};

// Aumentar cantidad de una zona
const aumentarCantidad = (zonaId) => {
    if (!cantidadesZonas.value[zonaId]) {
        cantidadesZonas.value[zonaId] = 0;
    }
    const zona = zonasDisponibles.value.find(z => z.id === zonaId);
    if (zona) {
        const disponibles = zona.tickets_disponibles || zona.capacidad_maxima;
        if (cantidadesZonas.value[zonaId] < disponibles) {
            cantidadesZonas.value[zonaId]++;
        }
    }
};

// Disminuir cantidad de una zona
const disminuirCantidad = (zonaId) => {
    if (cantidadesZonas.value[zonaId] && cantidadesZonas.value[zonaId] > 0) {
        cantidadesZonas.value[zonaId]--;
    }
};

// Obtener nombre de zona por ID
const obtenerNombreZona = (zonaId) => {
    const zona = zonasDisponibles.value.find(z => z.id == zonaId);
    return zona ? zona.nombre : '';
};

// Obtener precio de zona por ID
const obtenerPrecioZona = (zonaId) => {
    const zona = zonasDisponibles.value.find(z => z.id == zonaId);
    return zona ? parseFloat(zona.precio) : 0;
};

// Cargar evento
const cargarEvento = async () => {
    try {
        loading.value = true;
        error.value = null;

        const eventoNombre = route.params.nombre;
        const data = await eventosService.getEvento(eventoNombre);
        evento.value = data;

        // Preseleccionar la primera presentación si existe
        if (data.presentaciones && data.presentaciones.length > 0) {
            presentacionSeleccionada.value = data.presentaciones[0];
        }
    } catch (err) {
        console.error('Error cargando evento:', err);
        error.value = err.response?.data?.message || 'No se pudo cargar el evento';
    } finally {
        loading.value = false;
    }
};

// Agregar al carrito
const handleComprar = () => {
    if (!presentacionSeleccionada.value) {
        toast.error('Error', 'Por favor selecciona una presentación');
        return;
    }

    // Verificar que hay al menos una zona con cantidad mayor a 0
    const tieneSeleccion = Object.values(cantidadesZonas.value).some(c => c > 0);
    if (!tieneSeleccion) {
        toast.error('Error', 'Por favor selecciona al menos una zona');
        return;
    }

    // Preparar las zonas seleccionadas
    const zonasSeleccionadas = [];
    for (const [zonaId, cantidad] of Object.entries(cantidadesZonas.value)) {
        if (cantidad > 0) {
            const zona = zonasDisponibles.value.find(z => z.id == zonaId);
            if (zona) {
                zonasSeleccionadas.push({
                    id: zona.id,
                    nombre: zona.nombre,
                    precio: parseFloat(zona.precio),
                    cantidad: cantidad
                });
            }
        }
    }

    // Agregar al carrito
    addToCart(evento.value, presentacionSeleccionada.value, zonasSeleccionadas);
    
    // Resetear selección
    cantidadesZonas.value = {};
    
    toast.success('¡Agregado al carrito!', `Se agregaron ${zonasSeleccionadas.reduce((sum, z) => sum + z.cantidad, 0)} tickets`);
};

onMounted(() => {
    cargarEvento();
});
</script>

<template>
    <AppLayout :title="`${evento?.nombre || 'Evento'} - Detalles`">
        <!-- Loading State -->
        <div v-if="loading" class="min-h-screen py-20 bg-gray-50 dark:bg-gray-900">
            <div class="container mx-auto px-4">
                <div class="animate-pulse">
                    <div class="h-96 bg-gray-300 dark:bg-gray-700 rounded-3xl mb-8"></div>
                    <div class="h-8 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
                    <div class="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2"></div>
                </div>
            </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="min-h-screen py-20 bg-gray-50 dark:bg-gray-900">
            <div class="container mx-auto px-4 text-center">
                <AlertCircle :size="64" :stroke-width="1.5" class="mx-auto mb-4 text-red-500" />
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Error al cargar el evento</h2>
                <p class="text-gray-600 dark:text-gray-400 mb-6">{{ error }}</p>
                <RouterLink to="/eventos"
                    class="inline-flex items-center gap-2 px-6 py-3 bg-[#B3224D] text-white rounded-xl font-semibold hover:bg-[#8d1a3c] transition-colors">
                    <ArrowLeft :size="20" />
                    Volver a eventos
                </RouterLink>
            </div>
        </div>

        <!-- Evento Content -->
        <div v-else-if="evento" class="min-h-screen bg-gray-50 dark:bg-gray-900">
            <!-- Hero Section con Imagen -->
            <section class="relative h-[60vh] min-h-[500px] overflow-hidden">
                <!-- Imagen de fondo -->
                <div v-if="imagenPrincipal" class="absolute inset-0">
                    <img :src="imagenPrincipal" :alt="evento.nombre" class="w-full h-full object-cover" />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
                </div>
                <div v-else class="absolute inset-0 bg-gradient-to-br from-[#B3224D] to-[#8d1a3c]">
                    <component :is="iconoCategoria" :size="200" :stroke-width="1"
                        class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-white/20" />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
                </div>

                <!-- Contenido del Hero -->
                <div class="relative container mx-auto px-4 h-full flex flex-col justify-end pb-12">
                    <div class="max-w-4xl">
                        <!-- Breadcrumb -->
                        <div class="mb-4">
                            <RouterLink to="/eventos"
                                class="inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors">
                                <ArrowLeft :size="16" />
                                Volver a eventos
                            </RouterLink>
                        </div>

                        <!-- Badge de categoría y estado -->
                        <div class="flex flex-wrap gap-3 mb-4">
                            <span
                                class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm text-gray-900 dark:text-white shadow-lg">
                                <component :is="iconoCategoria" :size="16" :stroke-width="2" />
                                {{ evento.categoria || 'Evento' }}
                            </span>
                            <span v-if="evento.estado === '2'"
                                class="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-green-500 text-white shadow-lg">
                                <span class="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
                                Activo
                            </span>
                        </div>

                        <!-- Título -->
                        <h1 class="text-4xl md:text-6xl font-bold text-white mb-4 drop-shadow-lg">
                            {{ evento.nombre }}
                        </h1>

                        <!-- Información rápida -->
                        <div class="flex flex-wrap gap-6 text-white">
                            <div class="flex items-center gap-2">
                                <Calendar :size="20" :stroke-width="2" />
                                <span>{{ fechaFormateada }}</span>
                            </div>
                            <div v-if="evento.lugar" class="flex items-center gap-2">
                                <MapPin :size="20" :stroke-width="2" />
                                <span>{{ evento.lugar }}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <Tag :size="20" :stroke-width="2" />
                                <span>Desde {{ precioMinimo }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Contenido Principal -->
            <section class="container mx-auto px-4 py-12">
                <div class="grid lg:grid-cols-3 gap-8">
                    <!-- Columna Principal -->
                    <div class="lg:col-span-2 space-y-8">
                        <!-- Descripción -->
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
                            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <FileText :size="24" :stroke-width="2" class="text-[#B3224D]" />
                                Descripción del Evento
                            </h2>
                            <p class="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                                {{ evento.descripcion || 'No hay descripción disponible para este evento.' }}
                            </p>
                        </div>

                        <!-- Galería de imágenes -->
                        <div v-if="galeria.length > 0" class="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
                            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                                <ImageIcon :size="24" :stroke-width="2" class="text-[#B3224D]" />
                                Galería
                            </h2>
                            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                                <div v-for="(imagen, index) in galeria" :key="index"
                                    class="aspect-square rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-shadow cursor-pointer">
                                    <img :src="imagen" :alt="`Imagen ${index + 1}`"
                                        class="w-full h-full object-cover hover:scale-110 transition-transform duration-300" />
                                </div>
                            </div>
                        </div>

                        <!-- Información adicional -->
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
                            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                                <Info :size="24" :stroke-width="2" class="text-[#B3224D]" />
                                Información Adicional
                            </h2>
                            <div class="space-y-4">
                                <div v-if="evento.lugar" class="flex items-start gap-3">
                                    <MapPin :size="20" :stroke-width="2" class="text-[#B3224D] flex-shrink-0 mt-1" />
                                    <div>
                                        <p class="font-semibold text-gray-900 dark:text-white">Ubicación</p>
                                        <p class="text-gray-700 dark:text-gray-300">{{ evento.lugar }}</p>
                                    </div>
                                </div>
                                <div v-if="evento.duracion" class="flex items-start gap-3">
                                    <Clock :size="20" :stroke-width="2" class="text-[#B3224D] flex-shrink-0 mt-1" />
                                    <div>
                                        <p class="font-semibold text-gray-900 dark:text-white">Duración</p>
                                        <p class="text-gray-700 dark:text-gray-300">{{ evento.duracion }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Columna Lateral - Card de compra -->
                    <div class="lg:col-span-1">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg sticky top-24">
                            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Selecciona tu entrada</h3>
                            
                            <!-- Presentaciones -->
                            <div v-if="evento.presentaciones && evento.presentaciones.length > 0" class="mb-6">
                                <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                                    <Calendar :size="18" :stroke-width="2" class="text-[#B3224D]" />
                                    Fecha de presentación
                                </h4>
                                <div class="grid grid-cols-3 gap-2">
                                    <div
                                        v-for="(presentacion, index) in evento.presentaciones"
                                        :key="index"
                                        @click="seleccionarPresentacion(presentacion)"
                                        class="cursor-pointer rounded-lg p-3 text-center transition-all"
                                        :class="presentacionSeleccionada?.id === presentacion.id 
                                            ? 'bg-[#B3224D] text-white shadow-lg' 
                                            : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'"
                                    >
                                        <div class="text-2xl font-bold mb-1">
                                            {{ formatearDiaMes(presentacion.fecha).dia }}
                                        </div>
                                        <div class="text-xs font-semibold uppercase">
                                            {{ formatearDiaMes(presentacion.fecha).mes }}
                                        </div>
                                        <div class="text-xs mt-1 opacity-90">
                                            {{ presentacion.hora_inicio || 'Por confirmar' }}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Mensaje si no hay presentación seleccionada -->
                            <div v-if="!presentacionSeleccionada" class="text-center py-8 border-t border-gray-200 dark:border-gray-700">
                                <p class="text-sm text-gray-600 dark:text-gray-400">
                                    Selecciona una fecha para ver las zonas disponibles
                                </p>
                            </div>

                            <!-- Zonas disponibles de la presentación seleccionada -->
                            <div v-else-if="zonasDisponibles.length > 0" class="space-y-2 mb-6 border-t border-gray-200 dark:border-gray-700 pt-4">
                                <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Zonas disponibles</h4>
                                <div
                                    v-for="zona in zonasDisponibles"
                                    :key="zona.id"
                                    class="p-3 border-2 rounded-xl transition-all"
                                    :class="cantidadesZonas[zona.id] > 0
                                        ? 'border-[#B3224D] bg-[#B3224D]/5' 
                                        : 'border-gray-200 dark:border-gray-700'"
                                >
                                    <div class="flex items-center justify-between">
                                        <div class="flex-1">
                                            <h5 class="text-sm font-bold text-gray-900 dark:text-white"> ENTRADA {{ zona.nombre }}</h5>
                                            <p class="text-sm font-bold text-[#B3224D] dark:text-[#ff6b9d] mt-1">
                                                S/ {{ parseFloat(zona.precio).toFixed(2) }}
                                            </p>
                                        </div>
                                        
                                        <!-- Control de cantidad -->
                                        <div class="flex items-center gap-2">
                                            <button
                                                @click="disminuirCantidad(zona.id)"
                                                :disabled="!cantidadesZonas[zona.id] || cantidadesZonas[zona.id] === 0"
                                                class="w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-30 disabled:cursor-not-allowed font-bold text-gray-700 dark:text-gray-300 transition-colors"
                                            >
                                                -
                                            </button>
                                            <span class="w-8 text-center font-bold text-gray-900 dark:text-white">
                                                {{ cantidadesZonas[zona.id] || 0 }}
                                            </span>
                                            <button
                                                @click="aumentarCantidad(zona.id)"
                                                :disabled="cantidadesZonas[zona.id] >= (zona.tickets_disponibles || zona.capacidad_maxima)"
                                                class="w-8 h-8 rounded-lg bg-[#B3224D] hover:bg-[#8d1a3c] disabled:opacity-30 disabled:cursor-not-allowed font-bold text-white transition-colors"
                                            >
                                                +
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Mensaje si no hay zonas disponibles -->
                            <div v-else class="text-center py-8">
                                <AlertCircle :size="48" :stroke-width="1.5" class="mx-auto mb-3 text-yellow-500" />
                                <p class="text-gray-600 dark:text-gray-400">
                                    No hay zonas disponibles para esta presentación
                                </p>
                            </div>

                            <!-- Resumen y precio total -->
                            <div v-if="precioTotal > 0" class="border-t border-gray-200 dark:border-gray-700 pt-4 mb-6">
                                <div class="space-y-2 mb-3">
                                    <div v-for="(cantidad, zonaId) in cantidadesZonas" :key="zonaId" class="text-sm">
                                        <div v-if="cantidad > 0" class="flex justify-between text-gray-600 dark:text-gray-400">
                                            <span>{{ obtenerNombreZona(zonaId) }} x{{ cantidad }}</span>
                                            <span>S/ {{ (obtenerPrecioZona(zonaId) * cantidad).toFixed(2) }}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="flex justify-between items-center text-lg pt-3 border-t border-gray-200 dark:border-gray-700">
                                    <span class="font-semibold text-gray-700 dark:text-gray-300">Total:</span>
                                    <span class="text-2xl font-bold text-[#B3224D]">S/ {{ precioTotal.toFixed(2) }}</span>
                                </div>
                            </div>

                            <!-- Botones de acción -->
                            <button 
                                @click="handleComprar" 
                                :disabled="precioTotal === 0"
                                class="w-full flex items-center justify-center gap-2 px-6 py-4 bg-[#B3224D] text-white rounded-xl font-bold text-lg hover:bg-[#8d1a3c] transition-colors shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed mb-3"
                            >
                                <ShoppingCart :size="20" :stroke-width="2" />
                                Agregar al Carrito
                            </button>

                            <RouterLink
                                v-if="precioTotal > 0"
                                to="/carrito"
                                class="w-full flex items-center justify-center gap-2 px-6 py-3 border-2 border-[#B3224D] text-[#B3224D] dark:text-white rounded-xl font-semibold hover:bg-[#B3224D] hover:text-white transition-all"
                            >
                                Ver Carrito
                            </RouterLink>

                            <p v-if="precioTotal === 0" class="text-center text-sm text-gray-500 dark:text-gray-400">
                                Selecciona al menos una zona
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Toast Notification -->
        <ToastNotification ref="toastRef" />
    </AppLayout>
</template>

<style scoped>
/* Animaciones suaves */
.transition-all {
    transition: all 0.3s ease;
}
</style>
