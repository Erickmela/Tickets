<script setup>
import { ref } from "vue";

const props = defineProps({
    modelValue: String,
    placeholder: {
        type: String,
        default: "",
    },
    rows: {
        type: String,
        default: 4,
    },
    disabled: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(["update:modelValue"]);
const textareaRef = ref(null);

defineExpose({ focus: () => textareaRef.value?.focus() });
</script>

<template>
    <textarea
        ref="textareaRef"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        :rows="rows"
        :disabled="disabled"
        class="w-full text-sm p-3 bg-transparent border dark:text-white border-gray-300 rounded-sm shadow-sm outline-none dark:border-gray-600 focus:border-prim focus:ring-prim"
        :class="{
            'opacity-50 cursor-not-allowed': disabled,
        }"
    ></textarea>
</template>
