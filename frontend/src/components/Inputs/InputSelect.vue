<script setup>
defineProps({
    modelValue: {
        type: [String, Number, Boolean],
        default: "",
    },
});

defineEmits(["update:modelValue"]);
</script>

<template>
    <select
        :value="modelValue"
        @change="$emit('update:modelValue', $event.target.value)"
        class="w-full p-3 text-sm cursor-pointer bg-white dark:bg-gray-800 dark:text-white border border-gray-300 dark:border-gray-600 rounded-sm shadow-sm outline-none focus:border-prim focus:ring-prim"
    >
        <slot />
    </select>
</template>
