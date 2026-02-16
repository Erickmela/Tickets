<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import GuestLayout from '@/Layouts/GuestLayout.vue'
import InputLabel from '@/components/Inputs/InputLabel.vue'
import InputText from '@/components/Inputs/InputText.vue'
import InputError from '@/components/Inputs/InputError.vue'
import PrimaryButton from '@/components/Buttons/PrimaryButton.vue'
import { Loader2, ShieldCheck } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
    username: '',
    password: '',
    remember: false
})

const errors = ref({})
const loading = ref(false)
const generalError = ref('')

const handleSubmit = async () => {
    // Validaciones
    errors.value = {}
    generalError.value = ''

    if (!form.value.username || form.value.username.length < 3) {
        errors.value.username = 'El usuario es requerido'
        return
    }

    if (!form.value.password || form.value.password.length < 6) {
        errors.value.password = 'La contraseña debe tener al menos 6 caracteres'
        return
    }

    loading.value = true

    try {
        await authStore.login(form.value.username, form.value.password)

        // Verificar que NO sea un cliente
        if (authStore.userRole !== 'CLIENTE') {
            router.push('/admin/dashboard')
        } else {
            generalError.value = 'Acceso denegado. Use el login de clientes.'
            await authStore.logout()
        }
    } catch (err) {
        generalError.value = authStore.error || 'Usuario o contraseña incorrectos'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <GuestLayout>
        <!-- Icono y Título -->
        <div class="text-center mb-6">
            <h1 class="block text-2xl font-bold text-gray-900 dark:text-white">
                Panel de Trabajadores
            </h1>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Ingrese sus credenciales de acceso
            </p>
        </div>

        <!-- Formulario -->
        <form @submit.prevent="handleSubmit">
            <!-- Error General -->
            <div v-if="generalError"
                class="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg text-sm">
                {{ generalError }}
            </div>

            <!-- Usuario -->
            <div>
                <InputLabel for="username" value="Usuario" />
                <InputText id="username" v-model="form.username" type="text" class="mt-1 block w-full"
                    placeholder="usuario_admin" required autofocus :error="errors.username" />
                <InputError :message="errors.username" />
            </div>

            <!-- Contraseña -->
            <div class="mt-4">
                <InputLabel for="password" value="Contraseña" />
                <InputText id="password" v-model="form.password" type="password" class="mt-1 block w-full"
                    placeholder="••••••••" required :error="errors.password" />
                <InputError :message="errors.password" />
            </div>

            <!-- Recordarme -->
            <div class="block mt-5">
                <label class="flex items-center cursor-pointer">
                    <input v-model="form.remember" type="checkbox"
                        class="rounded border-gray-300 text-[#B3224D] shadow-sm focus:ring-[#B3224D]" />
                    <span class="ml-3 text-sm text-gray-600 dark:text-gray-400 select-none">
                        Recordar mi sesión
                    </span>
                </label>
            </div>

            <!-- Botón Submit -->
            <PrimaryButton type="submit" class="w-full mt-6 py-3 justify-center" :class="{ 'opacity-25': loading }"
                :disabled="loading">
                <Loader2 v-if="loading" class="w-5 h-5 animate-spin mr-3" />
                <span v-if="loading">Iniciando...</span>
                <span v-else>Acceder al Panel</span>
            </PrimaryButton>
        </form>

        <!-- Ayuda / Soporte -->
        <div class="mt-6 text-center">
            <p class="text-xs text-gray-500 dark:text-gray-400">
                ¿Problemas para acceder? Contacte al administrador del sistema
            </p>
        </div>

        <!-- Link a Login de Clientes -->
        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
                ¿Eres cliente?
                <router-link to="/login" class="text-[#B3224D] hover:text-[#8d1a3c] hover:underline font-semibold">
                    Ingresa aquí
                </router-link>
            </p>
        </div>
    </GuestLayout>
</template>
