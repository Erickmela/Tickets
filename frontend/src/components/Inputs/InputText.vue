<script setup>
import { onMounted, ref, computed } from "vue";
import { Eye, EyeOff } from "lucide-vue-next";

const props = defineProps({
    modelValue: [String, Number],
    type: {
        type: String,
        default: "text",
    },
    autofocus: {
        type: Boolean,
        default: false,
    },
});

defineEmits(["update:modelValue"]);

const input = ref(null);
const showPassword = ref(false);

// Determina el tipo de input actual
const inputType = computed(() => {
    if (props.type === "password") {
        return showPassword.value ? "text" : "password";
    }
    return props.type;
});

onMounted(() => {
    if (props.autofocus && input.value) {
        input.value.focus();
    }
});

defineExpose({ focus: () => input.value?.focus() });
</script>

<template>
    <div class="relative w-full">
        <input
            ref="input"
            :value="modelValue"
            :type="inputType"
            @input="$emit('update:modelValue', $event.target.value)"
            class="w-full text-sm p-3 bg-transparent border dark:text-white border-gray-300 rounded-sm shadow-sm outline-none dark:border-gray-600 focus:border-prim focus:ring-prim"
            :class="{ 'pr-11': props.type === 'password' }"
            v-bind="$attrs"
        />

        <button
            v-if="props.type === 'password'"
            type="button"
            @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-prim transition-colors"
        >
            <Eye v-if="!showPassword" class="w-5 h-5" />
            <EyeOff v-else class="w-5 h-5" />
        </button>
    </div>
</template>
