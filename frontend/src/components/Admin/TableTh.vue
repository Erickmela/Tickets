import { default } from '../../Pages/Admin/Perfil/Index.vue';
<script setup>
const props = defineProps({
    name: {
        type: String,
        default: ''
    }
})
</script>

<template>
    <th scope="col"
        class="px-4 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
        <template v-if="name">{{ name }}</template>
        <slot v-else></slot>
    </th>
</template>
