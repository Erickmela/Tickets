<script setup>
import { ref, computed } from 'vue';
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
import { User } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const usuariosStore = useUsuariosStore();

const toast = ref(null);
const toastHelper = useToasts(toast);

const form = ref({
    nombre_completo: authStore.user?.nombre_completo || '',
    telefono: authStore.user?.telefono || '',
    terms: false
});

const errors = ref({});
const cargando = ref(false);

const user = computed(() => authStore.user);

const submit = async () => {
    if (!form.value.terms) {
        toastHelper.error('Debe confirmar que sus datos son correctos');
        return;
    }

    cargando.value = true;
    errors.value = {};

    try {
        // Actualizar perfil del cliente autenticado (solo nombre_completo y telefono)
        await usuariosStore.updateMiPerfil({
            nombre_completo: form.value.nombre_completo,
            telefono: form.value.telefono
        });

        toastHelper.success('Perfil completado exitosamente');

        // Actualizar datos en authStore
        await authStore.refreshUser();

        // Redirigir al landing page
        setTimeout(() => {
            router.push({ name: 'home' });
        }, 1000);
    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            toastHelper.error('Error al completar el perfil');
        } else {
            toastHelper.error('Error al completar el perfil');
        }
    } finally {
        cargando.value = false;
    }
};

const logout = async () => {
    await authStore.logout();
    router.push({ name: 'home' });
};
</script>

<template>
    <GuestLayout max-width="lg">
        <ToastNotification ref="toast" />

        <div class="text-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                Completa tu perfil
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">
                ¡Bienvenido/a! {{ user?.email }}
            </p>
        </div>

        <form @submit.prevent="submit" class="space-y-4">
            <!-- DNI (solo lectura) -->
            <div>
                <InputLabel for="dni" value="DNI" />
                <InputText id="dni" :model-value="user?.dni" type="text"
                    class="bg-gray-100 dark:bg-gray-700 cursor-not-allowed" disabled readonly />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Este campo no se puede modificar</p>
            </div>

            <!-- Nombre Completo -->
            <div>
                <InputLabel for="nombre_completo" value="Nombre Completo *" />
                <InputText id="nombre_completo" v-model="form.nombre_completo" type="text"
                    placeholder="Juan Pérez García" required autofocus :error="errors.nombre_completo" />
                <InputError :message="errors.nombre_completo" />
            </div>

            <!-- Teléfono -->
            <div>
                <InputLabel for="telefono" value="Teléfono *" />
                <InputText id="telefono" v-model="form.telefono" type="text" maxlength="15" placeholder="987654321"
                    required :error="errors.telefono" />
                <InputError :message="errors.telefono" />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Para contactarte en caso de ser necesario
                </p>
            </div>

            <!-- Términos -->
            <div class="flex items-start">
                <div class="flex items-center h-5">
                    <input id="terms" v-model="form.terms" type="checkbox"
                        class="w-4 h-4 text-[#B3224D] bg-gray-100 border-gray-300 rounded focus:ring-[#B3224D] dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                        required />
                </div>
                <label for="terms" class="ml-2 text-sm text-gray-700 dark:text-gray-300 select-none cursor-pointer">
                    Confirmo que mis datos son correctos y completos
                </label>
            </div>

            <!-- Botones -->
            <div class="flex items-center justify-between pt-4">
                <button type="button" @click="logout"
                    class="text-sm text-gray-600 dark:text-gray-400 hover:text-[#B3224D] dark:hover:text-[#B3224D] font-medium hover:underline">
                    Cerrar sesión
                </button>

                <PrimaryButton type="submit" :disabled="cargando || !form.terms" class="min-w-40">
                    <span v-if="cargando">Guardando...</span>
                    <span v-else>Completar registro</span>
                </PrimaryButton>
            </div>
        </form>
    </GuestLayout>
</template>
