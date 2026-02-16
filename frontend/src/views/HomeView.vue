<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-purple-600 px-4">
    <div class="card max-w-4xl w-full">
      <h1 class="text-4xl font-bold text-center mb-4">Jala Jala Tickets</h1>
      <p class="text-center text-gray-600 mb-8">Sistema de gestión de tickets con seguridad anti-clonación</p>
      
      <div class="grid md:grid-cols-3 gap-4 mb-8">
        <div class="text-center p-4 bg-gray-50 rounded-lg">
          <div class="text-3xl mb-2">🎫</div>
          <h3 class="font-semibold">Tickets Únicos</h3>
          <p class="text-sm text-gray-600">Código UUID imposible de clonar</p>
        </div>
        <div class="text-center p-4 bg-gray-50 rounded-lg">
          <div class="text-3xl mb-2">📱</div>
          <h3 class="font-semibold">Validación QR</h3>
          <p class="text-sm text-gray-600">Control de acceso en tiempo real</p>
        </div>
        <div class="text-center p-4 bg-gray-50 rounded-lg">
          <div class="text-3xl mb-2">🔒</div>
          <h3 class="font-semibold">Seguro</h3>
          <p class="text-sm text-gray-600">Anti-clonación garantizada</p>
        </div>
      </div>
      
      <div class="text-center">
        <router-link to="/login" class="btn btn-primary btn-lg">
          Iniciar Sesión
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Home View - Landing page
</script>
