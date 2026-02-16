<script setup>
import { ref, watch } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputSelect from "@/components/Inputs/InputSelect.vue";
import InputError from "@/components/Inputs/InputError.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useUsuariosStore } from "@/stores/usuarios";

const emit = defineEmits(["close", "data_updated"]);
const props = defineProps({
    show: Boolean,
    data: Object,
});

const usuariosStore = useUsuariosStore();

function getFormData() {
    return {
        usuario: "",
        password: "",
        password_confirmation: "",
        dni: "",
        nombre_completo: "",
        email: "",
        telefono: "",
        rol: "VENDEDOR",
    };
}

const form = ref(getFormData());
const errors = ref({});
const toastForm = ref(null);
const toastGlobal = ref(null);
const toastFormHelper = useToasts(toastForm);
const toastGlobalHelper = useToasts(toastGlobal);
const cargando = ref(false);

const rolesOptions = [
    { value: "ADMIN", label: "Administrador" },
    { value: "VENDEDOR", label: "Vendedor" },
    { value: "VALIDADOR", label: "Validador" },
];

watch(
    () => props.data,
    (value) => {
        if (value) {
            form.value = {
                usuario: value.usuario || value.username || "",
                password: "",
                password_confirmation: "",
                dni: value.dni || "",
                nombre_completo: value.nombre_completo || "",
                email: value.email || "",
                telefono: value.telefono || "",
                rol: value.rol || "VENDEDOR",
            };
        }
    },
    { immediate: true }
);

const closeModal = () => {
    emit("close");
    limpiar();
};

const limpiar = () => {
    form.value = getFormData();
    errors.value = {};
};

const actualizarData = async () => {
    if (!props.data?.id) return;

    cargando.value = true;
    errors.value = {};

    try {
        const data = { ...form.value };

        // Si no se ingresó contraseña, no enviamos ni password ni password_confirmation
        if (!data.password) {
            delete data.password;
            delete data.password_confirmation;
        }

        await usuariosStore.updateTrabajador(props.data.id, data);
        toastGlobalHelper.success("Trabajador actualizado exitosamente");
        emit("data_updated");
        closeModal();
    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            toastFormHelper.error(
                error.response.data.message || "Error al actualizar el trabajador"
            );
        } else {
            toastFormHelper.error("Error al actualizar el trabajador");
        }
    } finally {
        cargando.value = false;
    }
};
</script>

<template>
    <DialogModal :show="show" @close="closeModal" max-width="3xl">
        <template #title>
            <div class="flex items-center space-x-2">
                <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>Editar Trabajador</span>
            </div>
        </template>

        <template #content>
            <ToastNotification ref="toastForm" />

            <form @submit.prevent="actualizarData" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Usuario -->
                    <div>
                        <InputLabel for="usuario" value="Usuario *" />
                        <InputText id="usuario" v-model="form.usuario" type="text" placeholder="usuario123"
                            :error="errors.usuario" />
                        <InputError :message="errors.usuario" />
                    </div>

                    <!-- DNI -->
                    <div>
                        <InputLabel for="dni" value="DNI *" />
                        <InputText id="dni" v-model="form.dni" type="text" maxlength="8" placeholder="12345678"
                            :error="errors.dni" />
                        <InputError :message="errors.dni" />
                    </div>

                    <!-- Contraseña (opcional) -->
                    <div>
                        <InputLabel for="password" value="Nueva Contraseña" />
                        <InputText id="password" v-model="form.password" type="password"
                            placeholder="Dejar en blanco para no cambiar" :error="errors.password" />
                        <InputError :message="errors.password" />
                    </div>

                    <!-- Confirmar Contraseña -->
                    <div>
                        <InputLabel for="password_confirmation" value="Confirmar Contraseña" />
                        <InputText id="password_confirmation" v-model="form.password_confirmation" type="password"
                            placeholder="Confirmar nueva contraseña" :error="errors.password_confirmation" />
                        <InputError :message="errors.password_confirmation" />
                    </div>

                    <!-- Nombre Completo -->
                    <div class="md:col-span-2">
                        <InputLabel for="nombre_completo" value="Nombre Completo *" />
                        <InputText id="nombre_completo" v-model="form.nombre_completo" type="text"
                            placeholder="Juan Pérez García" :error="errors.nombre_completo" />
                        <InputError :message="errors.nombre_completo" />
                    </div>

                    <!-- Email -->
                    <div>
                        <InputLabel for="email" value="Email" />
                        <InputText id="email" v-model="form.email" type="email" placeholder="juan@example.com"
                            :error="errors.email" />
                        <InputError :message="errors.email" />
                    </div>

                    <!-- Teléfono -->
                    <div>
                        <InputLabel for="telefono" value="Teléfono" />
                        <InputText id="telefono" v-model="form.telefono" type="text" placeholder="987654321"
                            :error="errors.telefono" />
                        <InputError :message="errors.telefono" />
                    </div>

                    <!-- Rol -->
                    <div class="md:col-span-2">
                        <InputLabel for="rol" value="Rol *" />
                        <InputSelect id="rol" v-model="form.rol" :options="rolesOptions" :error="errors.rol" />
                        <InputError :message="errors.rol" />
                    </div>
                </div>
            </form>
        </template>

        <template #footer>
            <div class="flex justify-end space-x-2">
                <ButtonCancel @click="closeModal" :disabled="cargando">
                    Cancelar
                </ButtonCancel>
                <ButtonSave @click="actualizarData" :disabled="cargando">
                    <span v-if="cargando">Actualizando...</span>
                    <span v-else>Actualizar Trabajador</span>
                </ButtonSave>
            </div>
        </template>
    </DialogModal>
</template>
