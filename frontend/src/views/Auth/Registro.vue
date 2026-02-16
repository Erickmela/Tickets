<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useUsuariosStore } from '@/stores/usuarios';
import { useToasts } from '@/Helpers/useToasts';
import GuestLayout from '@/Layouts/GuestLayout.vue';
import InputLabel from '@/components/Inputs/InputLabel.vue';
import InputText from '@/components/Inputs/InputText.vue';
import InputError from '@/components/Inputs/InputError.vue';
import PrimaryButton from '@/components/Buttons/PrimaryButton.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import { UserPlus, Loader2 } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const usuariosStore = useUsuariosStore();

const toast = ref(null);
const toastHelper = useToasts(toast);

const form = ref({
    dni: '',
    email: '',
    password: '',
    password_confirmation: '',
    terms: false
});

const errors = ref({});
const cargando = ref(false);

const submit = async () => {
    if (!form.value.terms) {
        toastHelper.error('Debes aceptar los términos y condiciones');
        return;
    }

    if (form.value.password !== form.value.password_confirmation) {
        errors.value.password_confirmation = 'Las contraseñas no coinciden';
        toastHelper.error('Las contraseñas no coinciden');
        return;
    }

    cargando.value = true;
    errors.value = {};

    try {
        // Registrar nuevo cliente (solo DNI + email + password)
        await usuariosStore.createCliente({
            dni: form.value.dni,
            email: form.value.email,
            password: form.value.password,
            password_confirmation: form.value.password_confirmation
        });

        toastHelper.success('Registro exitoso. Iniciando sesión...');

        // Auto-login con DNI y password ingresada
        setTimeout(async () => {
            try {
                await authStore.login(form.value.dni, form.value.password);
                // El navigation guard redirigirá a completar-perfil si falta nombre_completo/telefono
                router.push({ name: 'completar-perfil' });
            } catch (loginError) {
                toastHelper.error('Registro completado. Por favor inicia sesión');
                router.push({ name: 'login' });
            }
        }, 1500);

    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            const errorMsg = error.response.data.message ||
                error.response.data.dni?.[0] ||
                'Error al registrar';
            toastHelper.error(errorMsg);
        } else {
            toastHelper.error('Error al registrar. Intenta nuevamente');
        }
    } finally {
        cargando.value = false;
    }
};
</script>

<template>
    <GuestLayout max-width="lg">
        <ToastNotification ref="toast" />

        <div class="text-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                Crea tu cuenta
            </h1>
            <p class="mt-3 text-sm text-gray-600 dark:text-gray-400">
                ¿Ya tienes una cuenta?
                <router-link to="/login"
                    class="text-[#B3224D] hover:text-[#8d1a3c] dark:hover:text-[#8d1a3c] hover:underline decoration-2 font-semibold">
                    Inicia sesión aquí
                </router-link>
            </p>
        </div>

        <form @submit.prevent="submit" class="space-y-4">
            <!-- DNI y Email en la misma fila -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- DNI -->
                <div>
                    <InputLabel for="dni" value="DNI *" />
                    <InputText id="dni" v-model="form.dni" type="text" maxlength="8" placeholder="12345678" required
                        autofocus :error="errors.dni" />
                    <InputError :message="errors.dni" />
                </div>

                <!-- Email -->
                <div>
                    <InputLabel for="email" value="Email *" />
                    <InputText id="email" v-model="form.email" type="email" placeholder="juan@example.com" required
                        autocomplete="email" :error="errors.email" />
                    <InputError :message="errors.email" />
                </div>
            </div>

            <!-- Contraseña -->
            <div>
                <InputLabel for="password" value="Contraseña *" />
                <InputText id="password" v-model="form.password" type="password" placeholder="••••••••" required
                    autocomplete="new-password" :error="errors.password" />
                <InputError :message="errors.password" />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Mínimo 6 caracteres
                </p>
            </div>

            <!-- Confirmar Contraseña -->
            <div>
                <InputLabel for="password_confirmation" value="Confirmar Contraseña *" />
                <InputText id="password_confirmation" v-model="form.password_confirmation" type="password"
                    placeholder="••••••••" required autocomplete="new-password" :error="errors.password_confirmation" />
                <InputError :message="errors.password_confirmation" />
            </div>

            <!-- Términos y condiciones -->
            <div class="flex items-start">
                <div class="flex items-center h-5">
                    <input id="terms" v-model="form.terms" type="checkbox"
                        class="w-4 h-4 text-[#B3224D] bg-gray-100 border-gray-300 rounded focus:ring-[#B3224D] dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                        required />
                </div>
                <label for="terms" class="ml-2 text-sm text-gray-700 dark:text-gray-300 select-none cursor-pointer">
                    He leído y acepto los
                    <a href="#"
                        class="text-[#B3224D] hover:text-[#8d1a3c] dark:hover:text-[#8d1a3c] hover:underline decoration-2 font-semibold"
                        @click.prevent="toastHelper.info('Próximamente disponible')">
                        Términos de uso
                    </a>
                </label>
            </div>

            <!-- Botón de registro -->
            <PrimaryButton type="submit" :disabled="cargando || !form.terms" class="w-full py-3 justify-center">
                <Loader2 v-if="cargando" class="w-5 h-5 animate-spin mr-2" />
                <span v-if="cargando">Registrando...</span>
                <span v-else>Crear cuenta</span>
            </PrimaryButton>
        </form>

        <!-- Footer con links -->
        <div class="mt-6 text-center space-y-2">
            <p class="text-xs text-gray-600 dark:text-gray-400">
                ¿Eres trabajador del sistema?
                <router-link to="/admin/login"
                    class="text-[#B3224D] hover:text-[#8d1a3c] dark:hover:text-[#8d1a3c] hover:underline font-medium">
                    Accede aquí
                </router-link>
            </p>
        </div>
    </GuestLayout>
</template>
