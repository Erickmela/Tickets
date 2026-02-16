<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import {
    Menu,
    Bell,
    Search,
    Settings,
    LogOut,
    User,
    ChevronDown,
    ShoppingCart,
} from "lucide-vue-next";

const router = useRouter();
const authStore = useAuthStore();
const user = computed(() => authStore.user);
const userRole = computed(() => authStore.user?.rol || 'Usuario');

const props = defineProps({
    isSidebarOpen: Boolean,
    isMobile: Boolean,
});

const emit = defineEmits(["toggle-sidebar", "toggle-desktop-sidebar"]);

const showUserDropdown = ref(false);
const showNotifications = ref(false);

const toggleUserDropdown = () => {
    showUserDropdown.value = !showUserDropdown.value;
    showNotifications.value = false;
};

const toggleNotifications = () => {
    showNotifications.value = !showNotifications.value;
    showUserDropdown.value = false;
};

const handleSidebarToggle = () => {
    emit("toggle-sidebar");
};

const handleLogout = async () => {
    await authStore.logout();
    router.push('/');
};

// Cerrar dropdowns al hacer click fuera
const handleClickOutside = (event) => {
    const userDropdown = document.querySelector(".user-dropdown");
    const notificationDropdown = document.querySelector(
        ".notification-dropdown"
    );

    if (userDropdown && !userDropdown.contains(event.target)) {
        showUserDropdown.value = false;
    }

    if (notificationDropdown && !notificationDropdown.contains(event.target)) {
        showNotifications.value = false;
    }
};

onMounted(() => {
    document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
    document.removeEventListener("click", handleClickOutside);
});
</script>

<template>
    <header
        class="fixed top-0 left-0 right-0 z-40 bg-white dark:bg-gray-900 shadow-lg border-b border-gray-200 dark:border-gray-700">
        <div class="h-[70px] flex items-center justify-between px-4 md:px-6">
            <!-- Left Section -->
            <div class="flex items-center space-x-4">
                <!-- Mobile Menu Button -->
                <button v-if="isMobile" @click="handleSidebarToggle"
                    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                    <Menu class="w-6 h-6 text-gray-600 dark:text-gray-300" />
                </button>

                <!-- Logo -->
                <div class="flex items-center">
                    <router-link to="/" class="flex items-center space-x-2">
                        <div class="h-10 flex items-center justify-center">
                            <span class="text-xl font-bold text-primary-600">Jala Jala</span>
                        </div>
                    </router-link>
                </div>

                <!-- Desktop Menu Button -->
                <button v-if="!isMobile" @click="$emit('toggle-desktop-sidebar')"
                    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-600 dark:text-gray-300">
                    <Menu class="w-6 h-6" />
                </button>
            </div>

            <!-- Center Section - Search (Desktop) -->
            <div class="hidden md:flex flex-1 max-w-xl mx-8">
                <div class="flex-1 flex items-center justify-center">
                    <div class="relative flex items-center w-full sm:w-3/4">
                        <input type="text" placeholder="Aquí puede buscar algo"
                            class="pr-9 pl-4 py-2 text-sm bg-transparent border border-gray-300 dark:border-gray-800 text-gray-700 dark:text-gray-200 rounded-full w-full focus:outline-none focus:ring-0 focus:border-gray-800 dark:focus:border-gray-800 placeholder-gray-400 dark:placeholder-gray-500 transition-colors duration-200" />
                        <button type="submit" class="absolute right-4 text-gray-400 dark:text-gray-500 text-xl">
                            <Search class="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            <!-- Right Section -->
            <div class="flex items-center space-x-2">
                <!-- Mobile Search Button -->
                <button class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors md:hidden">
                    <Search class="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </button>


                <!-- User Profile Dropdown -->
                <div class="relative user-dropdown">
                    <button @click="toggleUserDropdown"
                        class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                        <img :src="user?.profile_photo_url || '/default-avatar.png'
                            " :alt="user?.name" class="w-8 h-8 rounded-full border-2 border-orange-500" />
                        <div class="hidden md:block text-left">
                            <p class="text-sm font-medium text-gray-900 dark:text-white">
                                {{ user?.name }}
                            </p>
                            <p class="text-xs text-gray-500 dark:text-gray-400 capitalize">
                                {{ userRole }}
                            </p>
                        </div>
                        <ChevronDown class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    </button>

                    <!-- User Dropdown Menu -->
                    <div v-if="showUserDropdown"
                        class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50">
                        <div class="p-2">
                            <router-link to="/perfil"
                                class="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                                <User class="w-4 h-4" />
                                <span>Mi Perfil</span>
                            </router-link>
                            <button @click="() => { }"
                                class="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg w-full text-left">
                                <Settings class="w-4 h-4" />
                                <span>Configuración</span>
                            </button>
                            <hr class="my-2 border-gray-200 dark:border-gray-700" />
                            <button @click="handleLogout"
                                class="flex items-center space-x-2 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg w-full text-left">
                                <LogOut class="w-4 h-4" />
                                <span>Cerrar Sesión</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </header>
</template>
