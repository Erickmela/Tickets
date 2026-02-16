/**
 * Rutas organizadas por rol y funcionalidad
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Inicio/Index.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/eventos',
      name: 'eventos',
      component: () => import('@/views/Inicio/Index.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Auth/ClienteLogin.vue'),
      meta: { requiresAuth: false, guestOnly: true }
    },
    {
      path: '/registro',
      name: 'registro',
      component: () => import('@/views/Auth/Registro.vue'),
      meta: { requiresAuth: false, guestOnly: true }
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/Auth/AdminLogin.vue'),
      meta: { requiresAuth: false, guestOnly: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/Admin/Dashboard/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN', 'VENDEDOR', 'VALIDADOR'] }
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('@/views/Admin/Dashboard/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN', 'VENDEDOR', 'VALIDADOR'] }
    },
    {
      path: '/completar-perfil',
      name: 'completar-perfil',
      component: () => import('@/views/Auth/CompletarPerfil.vue'),
      meta: { requiresAuth: true, requiresRole: ['CLIENTE'], skipProfileCheck: true }
    },
    {
      path: '/mis-tickets',
      name: 'mis-tickets',
      component: () => import('@/views/HomeView.vue'), 
      meta: { requiresAuth: true, requiresRole: ['CLIENTE'] }
    },    {
      path: '/admin/ventas',
      name: 'admin-ventas',
      component: () => import('../views/Admin/Ventas/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN', 'VENDEDOR'] }
    },
    {
      path: '/admin/ventas/crear',
      name: 'admin-ventas-crear',
      component: () => import('../views/Admin/Ventas/Crear.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN', 'VENDEDOR'] }
    },
    {
      path: '/admin/tickets',
      name: 'admin-tickets',
      component: () => import('../views/Admin/Tickets/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN', 'VENDEDOR'] }
    },
    {
      path: '/admin/eventos',
      name: 'admin-eventos',
      component: () => import('../views/Admin/Eventos/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN'] }
    },
    {
      path: '/admin/eventos/crear',
      name: 'admin-eventos-crear',
      component: () => import('../views/Admin/Eventos/Crear.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN'] }
    },
    {
      path: '/admin/eventos/:slug/editar',
      name: 'admin-eventos-editar',
      component: () => import('../views/Admin/Eventos/Editar.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN'] }
    },
    {
      path: '/admin/eventos/:slug/zonas',
      name: 'admin-zonas',
      component: () => import('../views/Admin/Zonas/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN'] }
    },
    {
      path: '/admin/usuarios',
      name: 'admin-usuarios',
      component: () => import('../views/Admin/Usuarios/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN'] }
    },
    {
      path: '/admin/trabajadores',
      name: 'admin-trabajadores',
      component: () => import('../views/Admin/Trabajadores/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['ADMIN'] }
    },
    {
      path: '/validar',
      name: 'validar',
      component: () => import('../views/Admin/Tickets/Partes/Validar.vue'),
      meta: { requiresAuth: true, requiresRole: ['VALIDADOR', 'ADMIN', 'VENDEDOR'] }
    },
    {
      path: '/admin/escaner',
      name: 'admin-escaner',
      component: () => import('../views/Admin/Escaner/Index.vue'),
      meta: { requiresAuth: true, requiresRole: ['VALIDADOR', 'ADMIN'] }
    },
    // {
    //   path: '/validaciones',
    //   name: 'validaciones',
    //   component: () => import('@/views/validador/ValidacionesView.vue'),
    //   meta: { requiresAuth: true, roles: ['VALIDADOR', 'ADMIN'] }
    // },
    // {
    //   path: '/reportes',
    //   name: 'reportes',
    //   component: () => import('@/views/admin/ReportesView.vue'),
    //   meta: { requiresAuth: true, roles: ['ADMIN'] }
    // },
  ]
})

// Navigation Guard - Verificar autenticación y permisos
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Inicializar auth si no está cargado
  if (!authStore.isAuthenticated && localStorage.getItem('user')) {
    await authStore.initializeAuth()
  }
  
  // Si la ruta es solo para guests y el usuario está autenticado
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    // Redirigir según el rol del usuario
    if (authStore.userRole === 'CLIENTE') {
      // Verificar si necesita completar perfil
      const user = authStore.user
      if (!user.nombre_completo || !user.telefono) {
        return next({ name: 'completar-perfil' })
      }
      return next({ name: 'mis-tickets' })
    } else {
      return next({ name: 'admin-dashboard' })
    }
  }
  
  // Si la ruta requiere autenticación y el usuario no está autenticado
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirigir al login apropiado según la ruta
    if (to.path.startsWith('/admin')) {
      return next({ name: 'admin-login', query: { redirect: to.fullPath } })
    } else {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
  }
  
  // Verificar permisos por rol
  if (to.meta.requiresRole && authStore.userRole) {
    if (!to.meta.requiresRole.includes(authStore.userRole)) {
      // Usuario sin permisos para esta ruta
      if (authStore.userRole === 'CLIENTE') {
        return next({ name: 'mis-tickets' })
      } else {
        return next({ name: 'admin-dashboard' })
      }
    }
  }
  
  // Verificar si el cliente necesita completar su perfil
  if (
    authStore.userRole === 'CLIENTE' && 
    authStore.isAuthenticated && 
    !to.meta.skipProfileCheck &&
    to.name !== 'completar-perfil'
  ) {
    const user = authStore.user
    // Si falta nombre_completo o teléfono, redirigir a completar perfil
    if (!user.nombre_completo || !user.telefono) {
      return next({ name: 'completar-perfil' })
    }
  }
  
  next()
})

export default router
