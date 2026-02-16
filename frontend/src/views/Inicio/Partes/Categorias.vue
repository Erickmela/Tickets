<script setup>
import { RouterLink } from "vue-router";
</script>

<template>
    <section class="py-16 bg-white dark:bg-gray-900">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-12">
                <h2 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                    Explora por Categoría
                </h2>
                <p class="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                    Encuentra el evento perfecto para ti
                </p>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                <!-- Música -->
                <RouterLink to="/eventos?categoria=musica" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#B3224D] to-[#8d1a3c] p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">🎵</div>
                    <h3 class="text-xl font-bold text-white">Música</h3>
                    <p class="text-white/80 text-sm">Conciertos y festivales</p>
                </RouterLink>

                <!-- Deportes -->
                <RouterLink to="/eventos?categoria=deportes" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-green-500 to-green-700 p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">⚽</div>
                    <h3 class="text-xl font-bold text-white">Deportes</h3>
                    <p class="text-white/80 text-sm">Partidos y competencias</p>
                </RouterLink>

                <!-- Teatro -->
                <RouterLink to="/eventos?categoria=teatro" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-500 to-purple-700 p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">🎭</div>
                    <h3 class="text-xl font-bold text-white">Teatro</h3>
                    <p class="text-white/80 text-sm">Obras y espectáculos</p>
                </RouterLink>

                <!-- Conferencias -->
                <RouterLink to="/eventos?categoria=conferencias" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">🎤</div>
                    <h3 class="text-xl font-bold text-white">Conferencias</h3>
                    <p class="text-white/80 text-sm">Talks y seminarios</p>
                </RouterLink>

                <!-- Festivales -->
                <RouterLink to="/eventos?categoria=festivales" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 to-orange-700 p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">🎪</div>
                    <h3 class="text-xl font-bold text-white">Festivales</h3>
                    <p class="text-white/80 text-sm">Eventos culturales</p>
                </RouterLink>

                <!-- Gastronomía -->
                <RouterLink to="/eventos?categoria=gastronomia" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-yellow-500 to-yellow-700 p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">🍽️</div>
                    <h3 class="text-xl font-bold text-white">Gastronomía</h3>
                    <p class="text-white/80 text-sm">Ferias y degustaciones</p>
                </RouterLink>

                <!-- Infantiles -->
                <RouterLink to="/eventos?categoria=infantiles" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-pink-500 to-pink-700 p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">🎈</div>
                    <h3 class="text-xl font-bold text-white">Infantiles</h3>
                    <p class="text-white/80 text-sm">Para toda la familia</p>
                </RouterLink>

                <!-- Otros -->
                <RouterLink to="/eventos" 
                    class="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-gray-500 to-gray-700 p-6 hover:scale-105 transition-transform cursor-pointer">
                    <div class="text-5xl mb-3">✨</div>
                    <h3 class="text-xl font-bold text-white">Más</h3>
                    <p class="text-white/80 text-sm">Ver todos</p>
                </RouterLink>
            </div>
        </div>
    </section>
</template>
