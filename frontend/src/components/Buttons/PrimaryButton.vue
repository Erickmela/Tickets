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
        class="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold tracking-widest text-white uppercase transition duration-150 ease-in-out border border-transparent rounded-md bg-[#B3224D] hover:bg-[#8d1a3c] focus:outline-none focus:ring-2 focus:ring-[#B3224D] focus:ring-offset-2 disabled:opacity-50"
    >
        <slot />
    </button>
</template>
