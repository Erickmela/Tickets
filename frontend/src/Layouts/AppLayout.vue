<script setup>
import { ref, provide, computed, watch } from "vue";
import { useRoute } from "vue-router";
import Navbar from "@/components/Navbar.vue";

const props = defineProps({
    title: {
        type: String,
        default: "Jala Jala Tickets"
    },
    description: {
        type: String,
        default: "La plataforma líder en venta de tickets para eventos. Descubre conciertos, festivales, conferencias y mucho más. Compra segura y validación anti-clonación."
    },
    showNavbar: {
        type: Boolean,
        default: true
    },
    showFooter: {
        type: Boolean,
        default: true
    }
});

const route = useRoute();
const pageTitle = computed(() => {
    return props.title ? `${props.title} - Jala Jala Tickets` : 'Jala Jala Tickets';
});

// Actualizar el título de la página
watch(pageTitle, (newTitle) => {
    document.title = newTitle;
}, { immediate: true });

// Actualizar meta tags
watch(() => props.description, (newDescription) => {
    let metaDescription = document.querySelector('meta[name="description"]');
    if (!metaDescription) {
        metaDescription = document.createElement('meta');
        metaDescription.name = 'description';
        document.head.appendChild(metaDescription);
    }
    metaDescription.content = newDescription;
}, { immediate: true });
</script>

<template>
    <div class="relative min-h-[100dvh] flex flex-col text-base bg-gradient-to-t from-[#B3224D]/10 to-white dark:from-gray-800 dark:to-gray-900">

        <Navbar v-if="showNavbar" />

        <div class="flex justify-center flex-grow w-full">
            <main class="w-full">
                <slot />
            </main>
        </div>

        <footer v-if="showFooter" class="bg-gray-900 text-white py-12">
            <div class="container mx-auto px-4 sm:px-6 lg:px-8">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div>
                        <h3 class="text-xl font-bold mb-4">Jala Jala Tickets</h3>
                        <p class="text-gray-400">La mejor plataforma para comprar tickets de eventos de forma segura.</p>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-4">Enlaces</h4>
                        <ul class="space-y-2 text-gray-400">
                            <li><router-link to="/" class="hover:text-white transition">Inicio</router-link></li>
                            <li><router-link to="/eventos" class="hover:text-white transition">Eventos</router-link></li>
                            <li><router-link to="/login" class="hover:text-white transition">Iniciar Sesión</router-link></li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-4">Contacto</h4>
                        <p class="text-gray-400">Email: info@jalajalatickets.com</p>
                        <p class="text-gray-400">Tel: +51 999 999 999</p>
                    </div>
                </div>
                <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
                    <p>&copy; 2026 Jala Jala Tickets. Todos los derechos reservados.</p>
                </div>
            </div>
        </footer>

    </div>
</template>
