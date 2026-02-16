<script setup>
import { ChevronRight } from "lucide-vue-next";

defineProps({
    name: {
        type: String,
        default: "",
    },
    flecha: {
        type: Boolean,
        default: false,
    },
    type: {
        type: String,
        default: "button",
    },
    traslate: {
        type: Boolean,
        default: false,
    },
});
</script>

<template>
    <button :type="type"
        class="group inline-flex items-center gap-3 px-4 sm:px-8 py-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white font-bold rounded-2xl hover:shadow-orange-500/20 hover:shadow-lg"
        :class="{ 'translate-x-1 duration-300': traslate, 'hover:scale-105': traslate }">
        <div v-if="name" class="flex items-center gap-2">
            {{ name }}
            <ChevronRight v-if="flecha" class="w-5 h-5 group-hover:translate-x-1" />
        </div>
        <template v-if="$slots.default">
            <slot />
        </template>
    </button>
</template>
