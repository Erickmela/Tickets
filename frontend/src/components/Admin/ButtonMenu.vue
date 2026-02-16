<script setup>
const props = defineProps({
    name: {
        type: String,
        default: "",
    },
    icon: {
        type: [Object, Function],
    },
    as: {
        type: [String, Object, Function],
        default: "button", // 'a', 'Link', etc.
    },
    href: {
        type: String,
        default: null,
    },
    target: {
        type: String,
        default: null,
    },
});
</script>

<template>
    <component
        :is="as"
        :href="href"
        :target="target"
        class="w-full flex items-center gap-2 text-left px-3 py-1.5 text-gray-500 dark:text-gray-400 hover:text-orange-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
        v-bind="$attrs"
    >
        <component :is="icon" class="w-4 h-4" />
        {{ name }}
    </component>
</template>
