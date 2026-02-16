<script setup>
defineProps({
    modelValue: {
        type: [String, Number, Boolean],
        default: "",
    },
    options: {
        type: Array,
        default: () => []
    },
    placeholder: {
        type: String,
        default: "Seleccione una opción"
    }
});

defineEmits(["update:modelValue"]);
</script>

<template>
    <select
        :value="modelValue"
        @change="$emit('update:modelValue', $event.target.value)"
        class="w-full p-3 text-sm cursor-pointer bg-white dark:bg-gray-800 dark:text-white border border-gray-300 dark:border-gray-600 rounded-sm shadow-sm outline-none focus:border-prim focus:ring-prim"
    >
        <!-- Si se usan opciones mediante prop -->
        <template v-if="options.length > 0">
            <option value="" disabled>{{ placeholder }}</option>
            <option v-for="option in options" :key="option.value" :value="option.value">
                {{ option.label }}
            </option>
        </template>
        <!-- Si se usan slots (método tradicional) -->
        <slot v-else />
    </select>
</template>
