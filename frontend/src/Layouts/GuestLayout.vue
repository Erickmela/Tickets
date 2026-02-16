<template>
    <div class="min-h-screen flex flex-col sm:justify-center items-center pt-6 sm:pt-0 bg-white dark:bg-gray-900">
        
        <div class="w-full px-6 py-4" :class="maxWidthClass">
            <!-- Logo / Título -->
            <div class="text-center mb-6">
                <router-link to="/">
                    <h1 class="text-4xl font-bold text-gray-900 dark:text-white">
                        Jala Jala Tickets
                    </h1>
                </router-link>
            </div>

            <!-- Contenido (Card) -->
            <div class="w-full bg-white dark:bg-gray-800 shadow-lg overflow-hidden sm:rounded-2xl px-8 py-10 border border-gray-200 dark:border-gray-700">
                <slot />
            </div>

            <!-- Footer -->
            <div class="mt-6 text-center">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                    © 2026 Jala Jala Tickets. Todos los derechos reservados.
                </p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';

// Layout para páginas de guest (sin autenticación)
const props = defineProps({
    maxWidth: {
        type: String,
        default: 'md' // md = 448px, lg = 512px, xl = 576px, 2xl = 672px
    }
});

const maxWidthClass = computed(() => {
    const widths = {
        'sm': 'sm:max-w-sm',
        'md': 'sm:max-w-md',
        'lg': 'sm:max-w-lg',
        'xl': 'sm:max-w-xl',
        '2xl': 'sm:max-w-2xl'
    };
    return widths[props.maxWidth] || 'sm:max-w-md';
});
</script>
