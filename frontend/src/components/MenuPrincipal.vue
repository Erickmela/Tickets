<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <router-link
      v-for="item in availableMenuItems"
      :key="item.name"
      :to="item.path"
      class="card hover:shadow-xl transition-shadow cursor-pointer"
    >
      <div class="flex items-center space-x-4">
        <div class="text-4xl">{{ item.icon }}</div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900">{{ item.title }}</h3>
          <p class="text-sm text-gray-500">{{ item.description }}</p>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const menuItems = [
  {
    name: 'ventas',
    path: '/ventas',
    icon: '💰',
    title: 'Ventas',
    description: 'Gestionar ventas de tickets',
    roles: ['VENDEDOR', 'ADMIN']
  },
  {
    name: 'nueva-venta',
    path: '/ventas/nueva',
    icon: '🎫',
    title: 'Nueva Venta',
    description: 'Crear una nueva venta',
    roles: ['VENDEDOR', 'ADMIN']
  },
  {
    name: 'validar',
    path: '/validar',
    icon: '📱',
    title: 'Validar Tickets',
    description: 'Escanear y validar tickets',
    roles: ['VALIDADOR', 'ADMIN']
  },
  {
    name: 'validaciones',
    path: '/validaciones',
    icon: '✅',
    title: 'Historial',
    description: 'Ver validaciones realizadas',
    roles: ['VALIDADOR', 'ADMIN']
  },
  {
    name: 'eventos',
    path: '/eventos',
    icon: '🎉',
    title: 'Eventos',
    description: 'Gestionar eventos y zonas',
    roles: ['ADMIN']
  },
  {
    name: 'reportes',
    path: '/reportes',
    icon: '📊',
    title: 'Reportes',
    description: 'Ver estadísticas y reportes',
    roles: ['ADMIN']
  }
]

const availableMenuItems = computed(() => {
  return menuItems.filter(item => 
    item.roles.includes(authStore.userRole)
  )
})
</script>
