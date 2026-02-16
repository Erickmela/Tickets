<script setup>
const props = defineProps({
    value: String,
});
</script>

<template>
    <label
        class="block font-medium text-sm mb-1 text-gray-700 dark:text-gray-400"
    >
        <span v-if="value">{{ value }} <span class="text-red-600">*</span></span>
        <span v-else><slot /></span>
    </label>
</template>
