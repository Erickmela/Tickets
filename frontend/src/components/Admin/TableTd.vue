<script setup>
const props = defineProps({
    contend: {
        type: [String, Number],
        default: ''
    }
})
</script>

<template>
    <td class="px-4 py-4 text-sm text-gray-500 dark:text-gray-400">
        <template v-if="contend">{{ contend }}</template>
        <slot v-else></slot>
    </td>
</template>
