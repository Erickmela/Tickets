<template>
    <!-- Barra superior de contacto -->
    <aside class="hidden lg:block py-3 bg-gray-900" aria-label="Información de contacto">
        <div class="container mx-auto flex justify-between items-center px-4 text-sm">
            <a
                href="mailto:info@jalajalatickets.com"
                class="text-gray-300 inline-flex items-center hover:text-[#B3224D] transition-colors"
            >
                <svg class="h-4 w-4 text-[#B3224D] mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                info@jalajalatickets.com
            </a>

            <div class="flex items-center gap-5">
                <a
                    href="tel:+51999999999"
                    class="text-gray-300 inline-flex items-center hover:text-[#B3224D] transition-colors"
                >
                    <svg class="h-4 w-4 text-[#B3224D] mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                    </svg>
                    <span>+51 999 999 999</span>
                </a>
            </div>
        </div>
    </aside>

    <!-- Navbar principal -->
    <nav
        class="sticky top-0 z-40 w-full bg-white dark:bg-gray-800 shadow-md dark:shadow-gray-900/50 transition-colors duration-300"
        aria-label="Menú principal"
    >
        <div class="container mx-auto p-4 flex justify-between items-center">
            <div class="flex items-center gap-10">
                <!-- Logo -->
                <RouterLink to="/" class="flex items-center space-x-3" aria-label="Ir al inicio">
                    <span class="text-4xl">🎫</span>
                    <div class="flex flex-col">
                        <span class="text-2xl font-bold text-[#B3224D] leading-none">Jala Jala</span>
                        <span class="text-xs text-gray-600 dark:text-gray-400 tracking-wider">TICKETS</span>
                    </div>
                </RouterLink>

                <!-- Menu Desktop -->
                <ul class="hidden lg:flex gap-6 items-center">
                    <li
                        v-for="(item, index) in menuItems"
                        :key="index"
                        class="relative"
                        @mouseenter="openMenu(index)"
                        @mouseleave="closeMenuWithDelay(index)"
                    >
                        <RouterLink
                            :to="item.link"
                            class="px-2 py-2 transition-all border-b-2 border-transparent hover:border-[#B3224D] text-gray-800 dark:text-gray-200 hover:text-[#B3224D] dark:hover:text-[#B3224D] flex items-center gap-2 font-medium"
                            :class="{
                                'border-[#B3224D]': activeMenuItem === index,
                            }"
                        >
                            {{ item.name }}
                            <div v-if="item.isLive" class="flex items-center ml-1">
                                <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                                <span class="ml-1 text-xs bg-red-500 text-white px-2 py-0.5 rounded-full font-medium">LIVE</span>
                            </div>
                        </RouterLink>
                    </li>
                </ul>
            </div>

            <!-- Acciones -->
            <div class="flex items-center gap-2">
                <!-- Búsqueda (opcional) -->
                <button
                    type="button"
                    class="hidden md:block p-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                    aria-label="Buscar eventos"
                >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                    </svg>
                </button>

                <div class="hidden lg:block border-r border-gray-300 dark:border-gray-700 pr-2 h-6 mr-2"></div>

                <!-- Desktop Auth -->
                <div class="hidden lg:flex items-center gap-4">
                    <template v-if="!isAuthenticated">
                        <RouterLink
                            to="/login"
                            class="text-gray-800 dark:text-gray-200 border border-[#B3224D] hover:bg-gray-100 dark:hover:bg-gray-800 px-4 py-2 rounded-lg transition-all font-medium"
                        >
                            Inicia sesión
                        </RouterLink>

                        <RouterLink
                            to="/eventos"
                            class="bg-[#B3224D] text-white font-semibold rounded-lg px-5 py-2 transition-all hover:bg-[#8d1a3c] shadow-md"
                        >
                            Compra tickets
                        </RouterLink>
                    </template>

                    <template v-else>
                        <!-- Menu de perfil -->
                        <div class="relative" @mouseenter="showProfileMenu = true" @mouseleave="showProfileMenu = false">
                            <button
                                type="button"
                                class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            >
                                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-[#B3224D] to-[#8d1a3c] flex items-center justify-center text-white font-bold shadow-lg">
                                    {{ userName.charAt(0).toUpperCase() }}
                                </div>
                                <svg class="w-4 h-4 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                </svg>
                            </button>

                            <!-- Dropdown -->
                            <transition name="fade">
                                <div
                                    v-if="showProfileMenu"
                                    class="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50"
                                >
                                    <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                                        <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ userName }}</p>
                                        <p class="text-xs text-[#B3224D] font-medium mt-1">{{ userRole }}</p>
                                    </div>

                                    <RouterLink
                                        to="/dashboard"
                                        class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                                    >
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
                                        </svg>
                                        <span>Dashboard</span>
                                    </RouterLink>

                                    <RouterLink
                                        v-if="userRole === 'CLIENTE'"
                                        to="/mis-tickets"
                                        class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                                    >
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
                                        </svg>
                                        <span>Mis Tickets</span>
                                    </RouterLink>

                                    <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>

                                    <button
                                        type="button"
                                        @click="handleLogout"
                                        class="flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors w-full"
                                    >
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                                        </svg>
                                        <span>Cerrar sesión</span>
                                    </button>
                                </div>
                            </transition>
                        </div>
                    </template>
                </div>

                <!-- Mobile Menu Button -->
                <button
                    type="button"
                    class="lg:hidden p-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                    @click="toggleMenu"
                    aria-label="Abrir menú de navegación"
                >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                    </svg>
                </button>
            </div>
        </div>
    </nav>

    <!-- Mobile Menu Drawer -->
    <transition name="slide">
        <div v-if="mobileMenuOpen" class="fixed inset-0 z-50" @click="closeMenu">
            <div
                class="fixed top-0 bottom-0 right-0 w-80 h-full p-6 bg-gradient-to-b from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 shadow-2xl border-l border-gray-200 dark:border-gray-700 overflow-y-auto"
                @click.stop
                role="dialog"
                aria-modal="true"
                aria-label="Menú móvil"
            >
                <!-- Close button -->
                <button
                    type="button"
                    class="mb-4 text-xl text-gray-800 dark:text-gray-200 hover:text-[#B3224D] transition-colors"
                    @click="closeMenu"
                    aria-label="Cerrar menú"
                >
                    ✕
                </button>

                <!-- User Profile Section (authenticated) -->
                <div
                    v-if="isAuthenticated"
                    class="mb-6 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
                >
                    <div class="flex flex-col items-center mb-4">
                        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-[#B3224D] to-[#8d1a3c] flex items-center justify-center mb-3 border-4 border-white dark:border-gray-600 shadow-lg">
                            <span class="text-white font-bold text-xl">{{ userName.charAt(0).toUpperCase() }}</span>
                        </div>
                        <div class="text-center">
                            <p class="font-semibold text-gray-900 dark:text-gray-100 text-base">{{ userName }}</p>
                            <p class="text-sm text-[#B3224D] font-medium">{{ userRole }}</p>
                        </div>
                    </div>

                    <nav class="flex flex-col gap-0 mt-4 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                        <RouterLink
                            to="/dashboard"
                            @click="closeMenu"
                            class="flex items-center gap-3 px-3 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors border-b border-gray-200 dark:border-gray-700"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
                            </svg>
                            <span class="text-sm font-medium">Dashboard</span>
                        </RouterLink>

                        <RouterLink
                            v-if="userRole === 'CLIENTE'"
                            to="/mis-tickets"
                            @click="closeMenu"
                            class="flex items-center gap-3 px-3 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors border-b border-gray-200 dark:border-gray-700"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
                            </svg>
                            <span class="text-sm font-medium">Mis Tickets</span>
                        </RouterLink>

                        <button
                            type="button"
                            @click="handleLogout"
                            class="flex items-center gap-3 px-3 py-3 w-full text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                            </svg>
                            <span class="text-sm font-medium">Cerrar sesión</span>
                        </button>
                    </nav>
                </div>

                <!-- Guest Section -->
                <div
                    v-else
                    class="mb-6 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
                >
                    <div class="text-center mb-4">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">¡Bienvenido!</h3>
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            Inicia sesión para acceder a más funciones.
                        </p>
                    </div>

                    <nav class="flex flex-col gap-2">
                        <RouterLink
                            to="/login"
                            @click="closeMenu"
                            class="flex items-center justify-center gap-3 px-4 py-3 bg-[#B3224D] hover:bg-[#8d1a3c] text-white rounded-lg transition-colors font-medium shadow-md"
                        >
                            <span class="text-sm">Iniciar sesión</span>
                        </RouterLink>

                        <RouterLink
                            to="/eventos"
                            @click="closeMenu"
                            class="flex items-center justify-center gap-3 px-4 py-3 border border-[#B3224D] text-[#B3224D] dark:text-[#B3224D] hover:bg-[#B3224D]/10 rounded-lg transition-colors font-medium"
                        >
                            <span class="text-sm">Ver Eventos</span>
                        </RouterLink>
                    </nav>
                </div>

                <!-- Menu Items -->
                <ul class="flex flex-col gap-2">
                    <li
                        v-for="(item, index) in menuItems"
                        :key="index"
                        class="border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                    >
                        <RouterLink
                            :to="item.link"
                            @click="closeMenu"
                            class="flex items-center justify-between py-3 px-2 text-base font-medium text-gray-900 dark:text-gray-100 hover:text-[#B3224D] hover:bg-[#B3224D]/5 border-l-4 border-transparent hover:border-[#B3224D] transition-all duration-200"
                        >
                            <span class="flex items-center gap-2">
                                {{ item.name }}
                                <div v-if="item.isLive" class="flex items-center">
                                    <div class="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse mr-1"></div>
                                    <span class="text-xs bg-red-500 text-white px-1.5 py-0.5 rounded-full font-medium">LIVE</span>
                                </div>
                            </span>
                        </RouterLink>
                    </li>
                </ul>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const mobileMenuOpen = ref(false)
const showProfileMenu = ref(false)
const activeMenuItem = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userName = computed(() => authStore.userName || 'Usuario')
const userRole = computed(() => authStore.userRole || 'Invitado')

const menuItems = computed(() => [
    { name: 'Inicio', link: '/' },
    { name: 'Eventos', link: '/eventos' },
    { name: 'Categorías', link: '/categorias' },
    { name: 'Nosotros', link: '/nosotros' },
    { name: 'Contacto', link: '/contacto' },
])

const closeMenuTimeouts = ref({})

const openMenu = (index) => {
    activeMenuItem.value = index
    clearTimeout(closeMenuTimeouts.value[index])
}

const closeMenuWithDelay = (index) => {
    closeMenuTimeouts.value[index] = setTimeout(() => {
        if (activeMenuItem.value === index) {
            activeMenuItem.value = null
        }
    }, 200)
}

const toggleMenu = () => {
    mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMenu = () => {
    mobileMenuOpen.value = false
}

const handleLogout = async () => {
    mobileMenuOpen.value = false
    showProfileMenu.value = false
    await authStore.logout()
    router.push('/')
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
    transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
    transform: translateX(100%);
    opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
    transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}
</style>
