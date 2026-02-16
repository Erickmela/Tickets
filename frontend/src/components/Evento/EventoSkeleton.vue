<script setup>
const props = defineProps({
    cantidad: {
        type: Number,
        default: 4
    }
});
</script>

<template>
    <div 
        v-for="i in cantidad" 
        :key="i"
        class="bg-white dark:bg-gray-900 rounded-3xl shadow-lg overflow-hidden animate-pulse"
    >
        <!-- Imagen skeleton -->
        <div class="h-64 bg-gray-200 dark:bg-gray-700"></div>

        <!-- Contenido skeleton -->
        <div class="p-6 space-y-4">
            <!-- Título -->
            <div class="space-y-2">
                <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded-lg w-3/4"></div>
                <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded-lg w-1/2"></div>
            </div>

            <!-- Info -->
            <div class="space-y-2">
                <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
                <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-between pt-4">
                <div class="space-y-1">
                    <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
                    <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
                </div>
                <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded-xl w-24"></div>
            </div>
        </div>
    </div>
</template>
