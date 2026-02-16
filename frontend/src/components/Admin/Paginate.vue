<script setup>
import { computed } from "vue";
import { getPaginationItems } from "@/Helpers/Pagination.js";
import { ChevronLeft, ChevronRight } from "lucide-vue-next";

const props = defineProps({
    pagination: {
        type: Object,
        required: true,
    },
    skeleton: {
        type: Boolean,
        default: true
    }
});

const emit = defineEmits(["page-changed"]);

const paginationItems = computed(() => getPaginationItems(props.pagination, false));

const goToPage = (page) => {
    if (!page || page === props.pagination.current_page) return;
    scrollUp();
    emit("page-changed", page);
};

const scrollUp = () => {
    setTimeout(() => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    }, 50);
};
</script>

<template>
    <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
        <div v-if="skeleton" class="flex flex-col sm:flex-row items-center justify-between gap-4 animate-pulse">
            <div class="h-4 w-48 bg-gray-200 dark:bg-gray-700 rounded"></div>

            <div class="flex items-center gap-2">
                <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>

                <div class="flex items-center gap-1">
                    <div v-for="i in 6" :key="i" class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                </div>

                <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            </div>
        </div>

        <div v-else class="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="text-sm text-gray-500 dark:text-gray-400">
                Mostrando <span class="font-medium">
                    {{ pagination.from ?? 0 }} a {{ pagination.to ?? 0 }}
                </span> de <span class="font-medium">{{ pagination.total ?? 0 }}</span> registros
            </div>

            <div class="flex items-center gap-2">
                <!-- Botón Anterior -->
                <button @click="goToPage(pagination.current_page - 1)" :disabled="pagination.current_page <= 1"
                    class="p-2 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <ChevronLeft class="w-4 h-4 text-gray-700 dark:text-white" />
                </button>

                <!-- Números de página -->
                <div class="flex items-center gap-1">
                    <template v-for="(item, index) in paginationItems" :key="index">
                        <span v-if="item.type === 'dots'" class="px-3 py-1.5 text-gray-400">...</span>
                        <button v-else @click="goToPage(item.value)" :class="[
                            'w-8 h-8 flex items-center justify-center text-sm rounded-lg transition-colors',
                            item.active
                                ? 'bg-orange-600 text-white'
                                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                        ]">
                            {{ item.value }}
                        </button>
                    </template>
                </div>

                <!-- Botón Siguiente -->
                <button @click="goToPage(pagination.current_page + 1)"
                    :disabled="pagination.current_page >= pagination.last_page"
                    class="p-2 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <ChevronRight class="w-4 h-4 text-gray-700 dark:text-white" />
                </button>
            </div>
        </div>
    </div>
    <pre>
</pre>
</template>
