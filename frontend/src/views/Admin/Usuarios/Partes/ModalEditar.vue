<script setup>
import { ref, watch } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputError from "@/components/Inputs/InputError.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useUsuariosStore } from "@/stores/usuarios";

const emit = defineEmits(["close", "data_updated"]);
const props = defineProps({
    show: Boolean,
    data: Object
});

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

watch(
    () => props.data,
    (value) => {
        if (value) {
            form.value = {
                dni: value.dni || "",
                nombre_completo: value.nombre_completo || "",
                email: value.email || "",
                telefono: value.telefono || "",
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
        await usuariosStore.updateCliente(props.data.id, form.value);
        toastGlobalHelper.success("Cliente actualizado exitosamente");
        emit("data_updated");
        closeModal();
    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            toastFormHelper.error(
                error.response.data.message || "Error al actualizar el cliente"
            );
        } else {
            toastFormHelper.error("Error al actualizar el cliente");
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
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>Editar Cliente</span>
            </div>
        </template>

        <template #content>
            <ToastNotification ref="toastForm" />

            <form @submit.prevent="actualizarData" class="space-y-4">
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
                <ButtonSave @click="actualizarData" :disabled="cargando">
                    <span v-if="cargando">Actualizando...</span>
                    <span v-else>Actualizar Cliente</span>
                </ButtonSave>
            </div>
        </template>
    </DialogModal>
</template>
