<script setup>
import { RouterLink } from 'vue-router';
import ButtonPrimary from '@/components/Buttons/ButtonPrimary.vue';

const props = defineProps({
    estadisticas: {
        type: Object,
        default: () => ({
            eventosActivos: 0,
            ticketsVendidos: 0,
            usuariosRegistrados: 0
        })
    }
});
</script>

<template>
    <section class="py-20 bg-gradient-to-br from-[#B3224D] to-[#8d1a3c] text-white relative overflow-hidden">
        <!-- Decoración de fondo -->
        <div class="absolute inset-0 opacity-10">
            <div class="absolute top-10 left-10 text-9xl">🎉</div>
            <div class="absolute bottom-10 right-10 text-9xl">🎊</div>
            <div class="absolute top-1/2 left-1/4 text-7xl">✨</div>
        </div>

        <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <!-- Estadísticas -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                <div class="text-center">
                    <div class="text-5xl font-bold mb-2">{{ estadisticas.eventosActivos }}+</div>
                    <div class="text-white/80">Eventos Activos</div>
                </div>
                <div class="text-center">
                    <div class="text-5xl font-bold mb-2">{{ estadisticas.ticketsVendidos }}+</div>
                    <div class="text-white/80">Tickets Vendidos</div>
                </div>
                <div class="text-center">
                    <div class="text-5xl font-bold mb-2">{{ estadisticas.usuariosRegistrados }}+</div>
                    <div class="text-white/80">Usuarios Felices</div>
                </div>
            </div>

            <!-- Call to Action -->
            <div class="text-center max-w-3xl mx-auto">
                <h2 class="text-4xl md:text-5xl font-bold mb-6">
                    ¿Listo para tu próxima aventura?
                </h2>
                <p class="text-xl mb-8 text-white/90">
                    Únete a miles de personas que ya disfrutan de los mejores eventos.
                    Compra tus tickets ahora y vive experiencias inolvidables.
                </p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <RouterLink to="/eventos">
                        <button class="px-8 py-4 bg-white text-[#B3224D] font-bold rounded-2xl hover:bg-gray-100 transition-all hover:scale-105 shadow-lg">
                            Explorar Eventos
                        </button>
                    </RouterLink>
                    <RouterLink to="/login">
                        <button class="px-8 py-4 bg-transparent border-2 border-white text-white font-bold rounded-2xl hover:bg-white/10 transition-all">
                            Crear Cuenta
                        </button>
                    </RouterLink>
                </div>
            </div>
        </div>
    </section>
</template>
