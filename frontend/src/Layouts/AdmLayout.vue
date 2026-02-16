<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useAuthStore } from "@/stores/auth";
import AdmSidebar from "@/components/AdmSidebar.vue";
import AdmHeader from "@/components/AdmHeader.vue";

const authStore = useAuthStore();
const user = computed(() => authStore.user);

const props = defineProps({
    title: String,
});

const isSidebarOpen = ref(false);
const isMobile = ref(false);
const isSidebarExpanded = ref(false);
const isHoveringOnSidebar = ref(false);

// Estado efectivo: expandido permanente O hover temporal
const isSidebarEffectivelyExpanded = computed(() => {
    return isSidebarExpanded.value || isHoveringOnSidebar.value;
});

const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value;
};

const toggleDesktopSidebar = () => {
    isSidebarExpanded.value = !isSidebarExpanded.value;
    localStorage.setItem("sidebar-expanded", JSON.stringify(isSidebarExpanded.value));
};

const handleSidebarExpand = (expanded) => {
    // Actualizar el estado de hover para que el main se ajuste
    if (!isMobile.value) {
        isHoveringOnSidebar.value = expanded;
    }
};

const checkMobile = () => {
    isMobile.value = window.innerWidth < 768;
    if (!isMobile.value) {
        isSidebarOpen.value = false;
    }
};

onMounted(() => {
    checkMobile();
    const savedSidebarState = localStorage.getItem('sidebar-expanded');
    if (savedSidebarState !== null) {
        isSidebarExpanded.value = JSON.parse(savedSidebarState);
    }
    window.addEventListener("resize", checkMobile);
});

onBeforeUnmount(() => {
    window.removeEventListener("resize", checkMobile);
});
</script>

<template>
    <div class="min-h-[100dvh] bg-gray-50 dark:bg-gray-900">
        <!-- Header -->
        <AdmHeader
            :is-sidebar-open="isSidebarOpen"
            :is-mobile="isMobile"
            @toggle-sidebar="toggleSidebar"
            @toggle-desktop-sidebar="toggleDesktopSidebar"
        />

        <!-- Sidebar -->
        <AdmSidebar
            :is-sidebar-open="isSidebarOpen"
            :is-sidebar-expanded="isSidebarExpanded"
            :is-mobile="isMobile"
            @toggle-sidebar="toggleSidebar"
            @sidebar-expand="handleSidebarExpand"
            :user="user"
        />

        <!-- Main Content -->
        <main
            class="transition-all duration-300 ease-in-out pt-[70px] min-h-[100dvh]"
            :class="{
                'ml-0': isMobile,
                'ml-64': !isMobile && isSidebarEffectivelyExpanded,
                'ml-20': !isMobile && !isSidebarEffectivelyExpanded,
            }"
        >
            <div class="p-4 md:p-6 max-w-full">
                <slot />
            </div>
        </main>

        <!-- Mobile Overlay -->
        <div
            v-if="isMobile && isSidebarOpen"
            class="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden transition-opacity duration-300"
            @click="toggleSidebar"
        ></div>
    </div>
</template>
