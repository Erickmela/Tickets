<script setup>
import { RouterLink } from "vue-router";
import { Ticket, Smartphone } from 'lucide-vue-next';
import ButtonPrimary from "@/components/Buttons/ButtonPrimary.vue";
import ButtonSecondary from "@/components/Buttons/ButtonSecondary.vue";
</script>

<template>
    <section
        class="relative overflow-hidden bg-white dark:bg-gray-900 py-20 md:py-24"
    >
        <!-- Íconos flotantes decorativos -->
        <div class="absolute inset-0 z-0 pointer-events-none overflow-hidden">
            <!-- Emoji decorativos de eventos -->
            <div class="absolute top-20 left-16 text-6xl opacity-20 animate-bounce" style="animation-duration: 3s;">🎫</div>
            <div class="absolute top-1/2 right-12 text-5xl opacity-20 animate-pulse" style="animation-duration: 4s;">🎵</div>
            <div class="absolute top-28 left-1/2 text-5xl opacity-20 animate-bounce" style="animation-duration: 3.5s;">🎤</div>
            <div class="absolute top-20 right-28 text-6xl opacity-20 animate-pulse" style="animation-duration: 3.2s;">🎸</div>
            <div class="absolute bottom-20 right-1/4 text-5xl opacity-20 animate-bounce" style="animation-duration: 3.8s;">🎭</div>
            <div class="absolute bottom-1/4 left-1/2 text-5xl opacity-20 animate-pulse" style="animation-duration: 4.2s;">🎪</div>
        </div>

        <!-- Contenido principal -->
        <div class="relative container mx-auto px-4 sm:px-6 lg:px-8 z-10">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div class="text-center lg:text-left">
                    <div class="inline-block mb-4">
                        <span class="text-[#B3224D] font-bold text-sm uppercase tracking-wider">Bienvenido</span>
                    </div>
                    <h1
                        class="text-4xl md:text-5xl lg:text-6xl font-semibold leading-tight text-gray-900 dark:text-white"
                    >
                        Vive experiencias
                        <br />
                        inolvidables con
                        <br />
                        <span
                            class="text-transparent font-sans font-bold bg-clip-text bg-gradient-to-r from-[#B3224D] to-[#8d1a3c]"
                        >
                            Jala Jala <br class="hidden lg:block" />
                            Tickets
                        </span>
                    </h1>
                    <p
                        class="text-md text-gray-600 dark:text-gray-300 my-10 max-w-lg mx-auto lg:mx-0"
                    >
                        Descubre los mejores eventos de música, teatro, deportes y más. 
                        Compra tus tickets de forma segura con tecnología anti-clonación.
                    </p>
                    <div
                        class="mt-8 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
                    >
                        <RouterLink to="/eventos">
                            <ButtonPrimary
                                name="Explorar Eventos"
                                :flecha="true"
                            />
                        </RouterLink>
                        <RouterLink to="/login">
                            <ButtonSecondary name="Iniciar Sesión" />
                        </RouterLink>
                    </div>
                </div>

                <div class="relative w-full flex justify-center select-none">
                    <!-- Imagen de héroe -->
                    <div class="relative w-full max-w-lg">
                        <!-- Círculo decorativo de fondo -->
                        <div class="absolute inset-0 bg-gradient-to-br from-[#B3224D]/20 to-purple-500/20 rounded-full blur-3xl"></div>
                        
                        <!-- Emoji grande central -->
                        <div class="relative flex items-center justify-center">
                            <div class="text-[20rem] leading-none select-none">
                                🎊
                            </div>
                        </div>
                        
                        <!-- Elementos flotantes alrededor -->
                        <div class="absolute -top-8 -left-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-4 animate-float">
                            <div class="flex items-center gap-3">
                                <div class="p-2 bg-[#B3224D]/10 rounded-lg">
                                    <Ticket :size="32" :stroke-width="2" class="text-[#B3224D]" />
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">Tickets</p>
                                    <p class="font-bold text-[#B3224D]">Seguros</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="absolute -bottom-4 -right-4 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-4 animate-float" style="animation-delay: 0.5s;">
                            <div class="flex items-center gap-3">
                                <div class="p-2 bg-[#B3224D]/10 rounded-lg">
                                    <Smartphone :size="32" :stroke-width="2" class="text-[#B3224D]" />
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">Validación</p>
                                    <p class="font-bold text-[#B3224D]">QR</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
@keyframes float {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-20px);
    }
}

.animate-float {
    animation: float 3s ease-in-out infinite;
}
</style>
