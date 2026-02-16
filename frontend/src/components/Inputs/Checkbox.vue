<script setup>
import { computed } from "vue";

const emit = defineEmits(["update:checked"]);

const props = defineProps({
    checked: {
        type: [Array, Boolean],
        default: false,
    },
    value: {
        type: String,
        default: null,
    },
});

const proxyChecked = computed({
    get() {
        return props.checked;
    },

    set(val) {
        emit("update:checked", val);
    },
});
</script>

<template>
    <input
        v-model="proxyChecked"
        type="checkbox"
        :value="value"
        class="rounded appearance-none outline-none border min-h-4 min-w-4 checked:bg-[#B3224D] checked:border-[#B3224D] border-gray-300 text-[#B3224D] shadow-sm focus:ring-[#B3224D]"
    />
</template>
