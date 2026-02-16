<script setup>
const props = defineProps({
    value: String,
    required: {
        type: Boolean,
        default: false
    }
});
</script>

<template>
    <label class="block text-sm text-gray-700 dark:text-gray-300 font-medium">
        <span v-if="value">{{ value }}</span>
        <span v-else>
            <slot />
        </span>

        <span v-if="required" class="text-red-500 dark:text-red-400 ml-1">*</span>
    </label>
</template>
