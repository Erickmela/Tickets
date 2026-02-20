<script setup>
import { ref, watch } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputSelect from "@/components/Inputs/InputSelect.vue";
import InputError from "@/components/Inputs/InputError.vue";
import InputImage from "@/components/Inputs/InputImage.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useCategoriasStore } from "@/stores/categorias";

const emit = defineEmits(["close", "data_updated"]);
const props = defineProps({
    show: Boolean,
    data: Object
});

const categoriasStore = useCategoriasStore();

function getFormData() {
    return {
        nombre: "",
        imagen_path: null,
        cat_estado: "",
    };
}

const form = ref(getFormData());
const imagenError = ref(null);
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
                nombre: value.nombre || "",
                imagen_path: null,
                cat_estado: value.cat_estado || "",
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
    imagenError.value = null;
};

const editarData = async () => {
    if (!props.data?.id) return;
    cargando.value = true;
    errors.value = {};
    imagenError.value = null;
    try {
        const data = new FormData();
        data.append("nombre", form.value.nombre);
        if (form.value.imagen_path) data.append("imagen_path", form.value.imagen_path);
        data.append("estado", form.value.estado);
        await categoriasStore.updateCategoria(props.data.id, data);
        toastGlobalHelper.success("Categoría actualizada exitosamente");
        emit("data_updated");
        closeModal();
    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            toastFormHelper.error(error.response.data.message || "Error al actualizar la categoría");
        } else {
            toastFormHelper.error("Error al actualizar la categoría");
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
                <span>Editar Categoría</span>
            </div>
        </template>
        <template #content>
            <ToastNotification ref="toastForm" />
            <form @submit.prevent="editarData" class="space-y-4">
                <div>
                    <InputLabel for="nombre" value="Nombre *" />
                    <InputText id="nombre" v-model="form.nombre" type="text" placeholder="Nombre de la categoría"
                        :error="errors.nombre" />
                    <InputError :message="errors.nombre" />
                </div>
                <div>
                    <InputLabel value="Imagen (opcional)" />
                    <InputImage v-model="form.imagen_path" :previewImage="props.data?.imagen_path || null"
                        :maxSizeMb="2" :accept="['image/jpeg', 'image/png', 'image/webp']"
                        @error="val => imagenError.value = val ? val[0] : null"
                        @cleared="() => imagenError.value = null" />
                    <InputError :message="imagenError || errors.imagen_path" />
                </div>
                <div>
                    <InputLabel for="estado" value="Estado" required />
                    <InputSelect v-model="form.estado" id="estado" class="mt-1 block w-full">
                        <option value="">Seleccione...</option>
                        <option value="1">Activado</option>
                        <option value="2">Desactivado</option>
                    </InputSelect>
                    <InputError :message="errors.cat_estado?.[0]" />
                </div>
            </form>
        </template>
        <template #footer>
            <div class="flex justify-end space-x-2">
                <ButtonCancel @click="closeModal" :disabled="cargando">
                    Cancelar
                </ButtonCancel>
                <ButtonSave @click="editarData" :disabled="cargando">
                    <span v-if="cargando">Actualizando...</span>
                    <span v-else>Actualizar Categoría</span>
                </ButtonSave>
            </div>
        </template>
    </DialogModal>
</template>
