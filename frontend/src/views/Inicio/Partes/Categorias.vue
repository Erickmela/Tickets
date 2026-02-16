<script setup>
import { RouterLink } from "vue-router";
import { Music, Trophy, Drama, Mic, Tent, Utensils, PartyPopper, Sparkles } from 'lucide-vue-next';

const categorias = [
    { 
        nombre: 'Música', 
        icono: Music,
        descripcion: 'Conciertos y festivales',
        ruta: '/eventos?categoria=musica',
        color: 'from-[#B3224D] to-[#8d1a3c]'
    },
    { 
        nombre: 'Deportes', 
        icono: Trophy,
        descripcion: 'Partidos y competencias',
        ruta: '/eventos?categoria=deportes',
        color: 'from-emerald-500 to-emerald-700'
    },
    { 
        nombre: 'Teatro', 
        icono: Drama,
        descripcion: 'Obras y espectáculos',
        ruta: '/eventos?categoria=teatro',
        color: 'from-purple-500 to-purple-700'
    },
    { 
        nombre: 'Conferencias', 
        icono: Mic,
        descripcion: 'Talks y seminarios',
        ruta: '/eventos?categoria=conferencias',
        color: 'from-blue-500 to-blue-700'
    },
    { 
        nombre: 'Festivales', 
        icono: Tent,
        descripcion: 'Eventos culturales',
        ruta: '/eventos?categoria=festivales',
        color: 'from-orange-500 to-orange-700'
    },
    { 
        nombre: 'Gastronomía', 
        icono: Utensils,
        descripcion: 'Ferias y degustaciones',
        ruta: '/eventos?categoria=gastronomia',
        color: 'from-amber-500 to-amber-700'
    },
    { 
        nombre: 'Infantiles', 
        icono: PartyPopper,
        descripcion: 'Para toda la familia',
        ruta: '/eventos?categoria=infantiles',
        color: 'from-pink-500 to-pink-700'
    },
    { 
        nombre: 'Más', 
        icono: Sparkles,
        descripcion: 'Ver todos',
        ruta: '/eventos',
        color: 'from-gray-500 to-gray-700'
    }
];

</script>

<template>
    <section class="py-20 bg-white dark:bg-gray-900">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <div class="inline-block mb-4">
                    <span class="text-[#B3224D] font-bold text-sm uppercase tracking-wider">Categorías</span>
                </div>
                <h2 class="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                    Explora por Categoría
                </h2>
                <p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                    Encuentra el evento perfecto para ti
                </p>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                <RouterLink 
                    v-for="(categoria, index) in categorias" 
                    :key="index"
                    :to="categoria.ruta" 
                    class="group relative overflow-hidden rounded-3xl bg-gradient-to-br p-8 hover:scale-105 hover:shadow-2xl transition-all duration-300 cursor-pointer"
                    :class="categoria.color"
                >
                    <!-- Efecto de brillo en hover -->
                    <div class="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
                    
                    <div class="relative z-10">
                        <div class="mb-4 transform group-hover:scale-110 transition-transform duration-300">
                            <component 
                                :is="categoria.icono" 
                                :size="56" 
                                :stroke-width="1.5"
                                class="text-white"
                            />
                        </div>
                        <h3 class="text-xl font-bold text-white mb-2">
                            {{ categoria.nombre }}
                        </h3>
                        <p class="text-white/90 text-sm">
                            {{ categoria.descripcion }}
                        </p>
                    </div>
                    
                    <!-- Flecha decorativa -->
                    <div class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all duration-300">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
                        </svg>
                    </div>
                </RouterLink>
            </div>
        </div>
    </section>
</template>
