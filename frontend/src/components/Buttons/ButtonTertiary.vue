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
        class="inline-flex items-center gap-3 px-4 sm:px-8 py-4 bg-white/20 backdrop-blur-sm border-2 border-white/30 text-white font-bold rounded-2xl hover:bg-white/30 shadow-xl"
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
