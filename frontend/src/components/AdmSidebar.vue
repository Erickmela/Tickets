<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import {
    LayoutDashboard,
    Users,
    Settings,
    ChevronDown,
    ShoppingCart,
    CheckCircle,
    CalendarDays,
    BarChart3,
    TicketPercent,
    Circle,
} from "lucide-vue-next";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const userRole = computed(() => authStore.user?.rol || '');

const hasPermission = (roles) => {
    if (!roles || roles.length === 0) return true;
    return roles.includes(userRole.value);
};

const props = defineProps({
    isSidebarOpen: Boolean,
    isMobile: Boolean,
    isSidebarExpanded: Boolean,
    user: Object,
});

const emit = defineEmits(["toggle-sidebar", "sidebar-expand"]);

const expandedMenus = ref({});
const isHovering = ref(false);

const toggleMenu = (menuKey) => {
    expandedMenus.value[menuKey] = !expandedMenus.value[menuKey];
};

const handleSidebarHover = (hovering) => {
    isHovering.value = hovering;
    if (!props.isMobile) {
        emit("sidebar-expand", hovering);
    }
};

const isActive = (itemRoute) => {
    if (!itemRoute) return false;
    return route.path === itemRoute || route.path.startsWith(itemRoute + '/');
};

const navigateTo = (path) => {
    router.push(path);
    if (props.isMobile) {
        emit("toggle-sidebar");
    }
};

const navItems = [
    {
        name: "Dashboard",
        icon: LayoutDashboard,
        route: "/dashboard",
        roles: ["ADMIN", "VENDEDOR", "VALIDADOR"],
    },
    {
        name: "Usuarios",
        icon: Users,
        route: "/usuarios",
        roles: ["ADMIN"],
        subItems: [
            {
                name: "Clientes",
                route: "/admin/usuarios",
                roles: ["ADMIN"],
            },
            {
                name: "Trabajadores",
                route: "/admin/trabajadores",
                roles: ["ADMIN"],
            },
        ],
    },
    {
        name: "Categorias",
        icon: CalendarDays,
        route: "/admin/categorias",
        roles: ["ADMIN"],
    },
    {
        name: "Eventos",
        icon: CalendarDays,
        route: "/admin/eventos",
        roles: ["ADMIN"],
    },
    {
        name: "Ventas",
        icon: ShoppingCart,
        roles: ["ADMIN", "VENDEDOR"],
        subItems: [
            {
                name: "Gestionar Ventas",
                route: "/admin/ventas",
                roles: ["ADMIN", "VENDEDOR"],
            },
        ],
    },
    {
        name: "Validaciones",
        icon: CheckCircle,
        roles: ["ADMIN", "VALIDADOR"],
        subItems: [
            {
                name: "Validar Ticket",
                route: "/validar",
               roles: ["ADMIN", "VALIDADOR"],
            },
            {
                name: "Escáner QR",
                route: "/admin/escaner",
                roles: ["ADMIN", "VALIDADOR"],
            },
        ],
    },
    {
        name: "Tickets",
        icon: TicketPercent,
        route: "/admin/tickets",
        roles: ["ADMIN", "VENDEDOR"],
    },
    {
        name: "Mis tickets",
        icon: TicketPercent,
        route: "/mis-tickets",
        roles: ["CLIENTE"],
    },
    {
        name: "Reportes",
        icon: BarChart3,
        route: "/admin/reportes",
        roles: ["ADMIN"],
    },
    {
        name: "Configuración",
        icon: Settings,
        route: "/configuracion",
        roles: ["ADMIN"],
    },
];

const visibleNavItems = computed(() => {
    return navItems.filter(item => {
        if (item.subItems) {
            const visibleSubs = item.subItems.filter(sub => hasPermission(sub.roles));
            return visibleSubs.length > 0;
        }
        return hasPermission(item.roles);
    });
});
</script>

<template>
    <aside
        @mouseenter="handleSidebarHover(true)"
        @mouseleave="handleSidebarHover(false)"
        :class="[
            'fixed top-[70px] left-0 h-[calc(100vh-70px)] bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ease-in-out z-30 shadow-lg',
            isMobile
                ? isSidebarOpen
                    ? 'translate-x-0 w-64'
                    : '-translate-x-full w-64'
                : isSidebarExpanded || isHovering
                    ? 'w-64'
                    : 'w-20',
        ]"
    >
        <div class="flex flex-col h-full overflow-hidden">
            <!-- Navigation -->
            <nav class="flex-1 overflow-y-auto py-4 px-3 custom-scrollbar">
                <ul class="space-y-1">
                    <li v-for="item in visibleNavItems" :key="item.name">
                        <!-- Menu with submenu -->
                        <div v-if="item.subItems">
                            <button
                                @click="toggleMenu(item.name)"
                                :class="[
                                    'flex items-center justify-between w-full px-3 py-2.5 rounded-lg transition-colors',
                                    'hover:bg-gray-100 dark:hover:bg-gray-800',
                                    isActive(item.route)
                                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                                        : 'text-gray-700 dark:text-gray-300',
                                ]"
                            >
                                <div class="flex items-center space-x-3 min-w-0">
                                    <component
                                        :is="item.icon"
                                        class="w-5 h-5 flex-shrink-0"
                                    />
                                    <span
                                        v-if="isSidebarExpanded || isHovering || isMobile"
                                        class="text-sm font-medium truncate"
                                    >
                                        {{ item.name }}
                                    </span>
                                </div>
                                <ChevronDown
                                    v-if="isSidebarExpanded || isHovering || isMobile"
                                    :class="[
                                        'w-4 h-4 transition-transform flex-shrink-0',
                                        expandedMenus[item.name] ? 'rotate-180' : '',
                                    ]"
                                />
                            </button>

                            <!-- Submenu -->
                            <transition
                                enter-active-class="transition duration-200 ease-out"
                                enter-from-class="opacity-0 -translate-y-1"
                                enter-to-class="opacity-100 translate-y-0"
                                leave-active-class="transition duration-150 ease-in"
                                leave-from-class="opacity-100 translate-y-0"
                                leave-to-class="opacity-0 -translate-y-1"
                            >
                                <ul
                                    v-if="
                                        expandedMenus[item.name] &&
                                        (isSidebarExpanded || isHovering || isMobile)
                                    "
                                    class="mt-1 space-y-1 ml-2"
                                >
                                    <li
                                        v-for="subItem in item.subItems.filter(sub => hasPermission(sub.roles))"
                                        :key="subItem.name"
                                    >
                                        <button
                                            @click="navigateTo(subItem.route)"
                                            :class="[
                                                'flex items-center space-x-3 w-full px-3 py-2 pl-11 rounded-lg transition-colors text-sm',
                                                isActive(subItem.route)
                                                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 font-medium'
                                                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
                                            ]"
                                        >
                                            <Circle
                                                :class="[
                                                    'w-2 h-2 flex-shrink-0',
                                                    isActive(subItem.route) ? 'fill-current' : '',
                                                ]"
                                            />
                                            <span class="truncate">{{ subItem.name }}</span>
                                        </button>
                                    </li>
                                </ul>
                            </transition>
                        </div>

                        <!-- Simple menu link -->
                        <button
                            v-else
                            @click="navigateTo(item.route)"
                            :class="[
                                'flex items-center space-x-3 w-full px-3 py-2.5 rounded-lg transition-colors',
                                isActive(item.route)
                                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 font-medium'
                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800',
                            ]"
                        >
                            <component
                                :is="item.icon"
                                class="w-5 h-5 flex-shrink-0"
                            />
                            <span
                                v-if="isSidebarExpanded || isHovering || isMobile"
                                class="text-sm truncate"
                            >
                                {{ item.name }}
                            </span>
                        </button>
                    </li>
                </ul>
            </nav>

            <!-- User info (Footer) -->
            <div
                v-if="user"
                class="border-t border-gray-200 dark:border-gray-700 p-4"
            >
                <div
                    class="flex items-center space-x-3"
                    :class="{ 'justify-center': !isSidebarExpanded && !isHovering && !isMobile }"
                >
                    <div
                        class="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-semibold flex-shrink-0"
                    >
                        {{ user.nombre_completo?.charAt(0).toUpperCase() || 'U' }}
                    </div>
                    <div
                        v-if="isSidebarExpanded || isHovering || isMobile"
                        class="flex-1 min-w-0"
                    >
                        <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {{ user.nombre_completo }}
                        </p>
                        <p class="text-xs text-gray-500 dark:text-gray-400 capitalize truncate">
                            {{ userRole }}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </aside>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #4a5568;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #718096;
}
</style>
