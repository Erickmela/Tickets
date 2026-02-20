<script setup>
defineProps({
    type: {
        type: String,
        default: "submit",
    },
});
</script>

<template>
    <button :type="type"
        class="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold tracking-widest text-white uppercase transition duration-150 ease-in-out border border-transparent rounded-md bg-gradient-to-r from-primary-500 to-primary-600 hover:shadow-orange-700/20 hover:shadow-lg focus:outline-none focus:ring-offset-2 disabled:opacity-50 hover:opacity-85">
        <slot />
    </button>
</template>
