<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import GuestLayout from '@/Layouts/GuestLayout.vue'
import InputLabel from '@/components/Inputs/InputLabel.vue'
import InputText from '@/components/Inputs/InputText.vue'
import InputError from '@/components/Inputs/InputError.vue'
import PrimaryButton from '@/components/Buttons/PrimaryButton.vue'
import { Loader2 } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
    dni: '',
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

    if (!form.value.dni || form.value.dni.length !== 8 || !/^\d+$/.test(form.value.dni)) {
        errors.value.dni = 'El DNI debe tener 8 dígitos numéricos'
        return
    }

    if (!form.value.password || form.value.password.length < 6) {
        errors.value.password = 'La contraseña debe tener al menos 6 caracteres'
        return
    }

    loading.value = true

    try {
        await authStore.login(form.value.dni, form.value.password)

        // Verificar que sea un cliente
        if (authStore.userRole === 'CLIENTE') {
            router.push('/mis-tickets')
        } else {
            generalError.value = 'Acceso denegado. Use el login de trabajadores.'
            await authStore.logout()
        }
    } catch (err) {
        generalError.value = authStore.error || 'DNI o contraseña incorrectos'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <GuestLayout>
        <!-- Título y Subtítulo -->
        <div class="text-center mb-6">
            <h1 class="block text-2xl font-bold text-gray-900 dark:text-white">
                Iniciar sesión
            </h1>
            <p class="mt-3 text-sm text-gray-600 dark:text-gray-400">
                ¿Aún no tienes una cuenta?
                <router-link to="/registro"
                    class="text-[#B3224D] hover:text-[#8d1a3c] hover:underline decoration-2 font-semibold">
                    Regístrate aquí
                </router-link>
            </p>
        </div>

        <!-- Future: Google Login -->
        <!-- <div>
            <CardGoogle />
        </div>

        <div class="w-full flex justify-between items-center">
            <hr class="my-7 h-px border-0 bg-gray-200 dark:bg-gray-600 flex-1" />
            <div class="text-gray-600 dark:text-gray-400 text-xs leading-[18px] px-2.5">
                O
            </div>
            <hr class="my-7 h-px border-0 bg-gray-200 dark:bg-gray-600 flex-1" />
        </div> 

        <!-- Formulario -->
        <form @submit.prevent="handleSubmit">
            <!-- Error General -->
            <div v-if="generalError"
                class="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg text-sm">
                {{ generalError }}
            </div>

            <!-- DNI -->
            <div>
                <InputLabel for="dni" value="DNI" />
                <InputText id="dni" v-model="form.dni" type="text" maxlength="8" class="mt-1 block w-full"
                    placeholder="12345678" required autofocus :error="errors.dni" />
                <InputError :message="errors.dni" />
            </div>

            <!-- Contraseña -->
            <div class="mt-4">
                <div class="flex justify-between items-center">
                    <InputLabel for="password" value="Contraseña" />
                    <router-link to="/recuperar-contrasena"
                        class="text-sm text-[#B3224D] font-semibold decoration-2 hover:text-[#8d1a3c] hover:underline">
                        ¿Olvidó su contraseña?
                    </router-link>
                </div>
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
                        Recordarme
                    </span>
                </label>
            </div>

            <!-- Botón Submit -->
            <PrimaryButton type="submit" class="w-full mt-6 py-3 justify-center" :class="{ 'opacity-25': loading }"
                :disabled="loading">
                <Loader2 v-if="loading" class="w-5 h-5 animate-spin mr-3" />
                <span v-if="loading">Iniciando...</span>
                <span v-else>Iniciar sesión</span>
            </PrimaryButton>
        </form>

        <!-- Link a Login de Trabajadores -->
        <div class="mt-6 text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
                ¿Eres trabajador?
                <router-link to="/admin/login"
                    class="text-[#B3224D] hover:text-[#8d1a3c] hover:underline font-semibold">
                    Ingresa aquí
                </router-link>
            </p>
        </div>
    </GuestLayout>
</template>
