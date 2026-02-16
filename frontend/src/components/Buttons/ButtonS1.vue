<script setup>
defineProps({
    type: {
        type: String,
        default: "submit",
    },
});
</script>

<template>
    <button
        :type="type"
        class="px-3 py-1.5 text-sm font-medium rounded-lg bg-[#B3224D] text-white hover:bg-[#8d1a3c] flex items-center"
    >
        <slot />
    </button>
</template>
