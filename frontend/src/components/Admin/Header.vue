<script setup>
const props = defineProps({
    title: {
        type: String,
        default: ''
    },
    description: {
        type: String,
        default: ''
    },
    icon: {
        type: [Object, Function],
        default: ''
    }
})
</script>

<template>
    <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div class="px-6 py-4 bg-gradient-to-r from-orange-50 to-orange-100 dark:from-gray-800 dark:to-gray-800">
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                    <h1 class="text-xl md:text-2xl font-bold text-gray-800 dark:text-white flex items-center">
                        <component :is="icon" class="w-6 h-6 mr-2 text-orange-600 dark:text-orange-400"></component>
                        {{ props.title }}
                    </h1>
                    <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">{{ props.description }}</p>
                </div>

                <div class="flex items-center space-x-2 shrink-0">
                    <slot name="actions" />
                </div>
            </div>
        </div>
    </div>
</template>
