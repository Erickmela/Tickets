<script setup>
import { ref } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputError from "@/components/Inputs/InputError.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useUsuariosStore } from "@/stores/usuarios";

const emit = defineEmits(["close", "data_created"]);
const props = defineProps({ show: Boolean });

const usuariosStore = useUsuariosStore();

function getFormData() {
    return {
        dni: "",
        nombre_completo: "",
        email: "",
        telefono: "",
    };
}

const form = ref(getFormData());
const errors = ref({});
const toastForm = ref(null);
const toastGlobal = ref(null);
const toastFormHelper = useToasts(toastForm);
const toastGlobalHelper = useToasts(toastGlobal);
const cargando = ref(false);

const closeModal = () => {
    emit("close");
    limpiar();
};

const limpiar = () => {
    form.value = getFormData();
    errors.value = {};
};

const crearData = async () => {
    cargando.value = true;
    errors.value = {};

    try {
        await usuariosStore.createCliente(form.value);
        toastGlobalHelper.success("Cliente creado exitosamente");
        emit("data_created");
        closeModal();
    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            toastFormHelper.error(
                error.response.data.message || "Error al crear el cliente"
            );
        } else {
            toastFormHelper.error("Error al crear el cliente");
        }
    } finally {
        cargando.value = false;
    }
};
</script>

<template>
    <DialogModal :show="show" @close="closeModal" max-width="2xl">
        <template #title>
            <div class="flex items-center space-x-2">
                <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                <span>Agregar Nuevo Cliente</span>
            </div>
        </template>

        <template #content>
            <ToastNotification ref="toastForm" />

            <form @submit.prevent="crearData" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- DNI -->
                    <div>
                        <InputLabel for="dni" value="DNI *" />
                        <InputText id="dni" v-model="form.dni" type="text" maxlength="8" placeholder="12345678"
                            :error="errors.dni" />
                        <InputError :message="errors.dni" />
                    </div>

                    <!-- Nombre Completo -->
                    <div>
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
                </div>
            </form>
        </template>

        <template #footer>
            <div class="flex justify-end space-x-2">
                <ButtonCancel @click="closeModal" :disabled="cargando">
                    Cancelar
                </ButtonCancel>
                <ButtonSave @click="crearData" :disabled="cargando">
                    <span v-if="cargando">Creando...</span>
                    <span v-else>Crear Cliente</span>
                </ButtonSave>
            </div>
        </template>
    </DialogModal>
</template>
