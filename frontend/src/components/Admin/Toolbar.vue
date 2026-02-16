<script setup>
import { computed } from "vue";
import { Search } from "lucide-vue-next";

const props = defineProps({
    itemsPerPage: {
        type: Number,
        default: 10,
    },
    filterSearch: {
        type: String,
        default: "",
    },
    placeholder: {
        type: String,
        default: "Buscar...",
    },
    pageSizeOptions: {
        type: Array,
        default: () => [10, 25, 50, 100],
    },
});

const emit = defineEmits(["searchText", "itemsPerPage"]);

const localSearchQuery = computed({
    get: () => props.filterSearch,
    set: (value) => emit("searchText", value),
});
const localItemsPerPage = computed({
    get: () => props.itemsPerPage,
    set: (value) => emit("itemsPerPage", value),
});
</script>

<template>
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <!-- Búsqueda -->
            <div class="relative flex-1 w-full md:max-w-md">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search class="h-4 w-4 text-gray-400 dark:text-gray-500" />
                </div>
                <input type="text" v-model="localSearchQuery" :placeholder="placeholder"
                    class="block w-full pl-10 pr-3 py-2 rounded-lg text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 placeholder-gray-500 dark:placeholder-gray-400 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400" />
            </div>

            <!-- Controles -->
            <div class="flex flex-wrap items-center gap-3">
                <slot name="left-filters" />

                <div class="relative">
                    <select v-model="localItemsPerPage"
                        class="pl-3 pr-8 py-2 rounded-lg text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400">
                        <option v-for="option in pageSizeOptions" :value="option">
                            {{ option }} por página
                        </option>
                    </select>
                </div>

                <slot name="right-filters" />
            </div>
        </div>
    </div>
</template>
