<script setup>
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { Frown } from 'lucide-vue-next';
import EventoItem from "@/components/Evento/EventoItem.vue";
import EventoSkeleton from "@/components/Evento/EventoSkeleton.vue";
import ButtonPrimary from "@/components/Buttons/ButtonPrimary.vue";
import { eventosService } from "@/services/eventosService";

const props = defineProps({
    n_eventos: {
        type: Number,
        default: 8,
    },
});

const eventos = ref([]);
const NumSkeleton = props.n_eventos;
const StateSkeleton = ref(false);

const fetchEventos = async () => {
    try {
        StateSkeleton.value = true;
        // Obtener eventos activos y próximos
        const response = await eventosService.getEventosActivos();
        if (Array.isArray(response)) {
            // Tomar solo la cantidad especificada
            eventos.value = response.slice(0, props.n_eventos);
        } else {
            eventos.value = [];
        }
    } catch (error) {
        if (error.response?.status === 403) {
            console.warn('Acceso denegado a eventos. Asegúrate de que el backend permita acceso público.');
        } else if (error.response?.status === 404) {
            console.info('No hay eventos disponibles.');
        } else {
            console.error("Error al cargar los eventos:", error.message);
        }
        eventos.value = [];
    } finally {
        setTimeout(() => {
            StateSkeleton.value = false;
        }, 500);
    }
};

// Cargar eventos iniciales
onMounted(() => fetchEventos());
</script>

<template>
    <section id="eventos-nuevos" class="py-20 bg-white dark:bg-gray-900">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="flex flex-col md:flex-row justify-between items-center mb-12">
                <div>
                    <div class="inline-block mb-4">
                        <span class="text-[#B3224D] font-bold text-sm uppercase tracking-wider">
                            Próximos eventos
                        </span>
                    </div>
                    <h2 class="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">
                        Nuevos
                        <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#B3224D] to-[#8d1a3c]">
                            lanzamientos
                        </span>
                    </h2>
                </div>
                <RouterLink to="/eventos" class="hidden lg:block mt-4 md:mt-0">
                    <ButtonPrimary name="Ver todos los eventos" :flecha="true" />
                </RouterLink>
            </div>

            <!-- Mensaje sin eventos -->
            <div v-if="eventos.length === 0 && !StateSkeleton"
                class="text-center py-16 bg-gray-50 dark:bg-gray-800 rounded-3xl shadow-sm">
                <Frown :size="64" :stroke-width="1.5" class="mx-auto mb-4 text-[#B3224D]" />
                <h3 class="text-xl font-medium text-gray-900 dark:text-gray-200">
                    No se encontraron eventos nuevos
                </h3>
                <p class="mt-2 text-gray-600 dark:text-gray-400">
                    Pronto tendremos nuevos eventos disponibles
                </p>
            </div>

            <!-- Grid de eventos -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                <!-- Skeleton cargando -->
                <EventoSkeleton v-if="StateSkeleton" :cantidad="NumSkeleton" />

                <!-- Eventos cargados -->
                <template v-else>
                    <EventoItem v-for="evento in eventos" :key="evento.id" :evento="evento" />
                </template>
            </div>

            <!-- Botón móvil -->
            <div class="lg:hidden mt-12 flex justify-center items-center">
                <RouterLink to="/eventos">
                    <ButtonPrimary name="Ver todos los eventos" :flecha="true" />
                </RouterLink>
            </div>
        </div>
    </section>
</template>
