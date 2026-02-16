<script setup>
import { ref, watch } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputTextarea from "@/components/Inputs/InputTextarea.vue";
import InputError from "@/components/Inputs/InputError.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useEventosStore } from "@/stores/eventos";

const emit = defineEmits(["close", "data_updated"]);
const props = defineProps({
    show: Boolean,
    data: Object,
    eventoId: Number,
});

const eventosStore = useEventosStore();

function getFormData() {
    return {
        nombre: "",
        descripcion: "",
        precio: "",
        capacidad: "",
        activo: true,
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
    (newData) => {
        if (newData) {
            form.value = {
                nombre: newData.nombre || "",
                descripcion: newData.descripcion || "",
                precio: newData.precio || "",
                capacidad: newData.capacidad || "",
                activo: newData.activo !== undefined ? newData.activo : true,
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
        const dataToSend = {
            nombre: form.value.nombre,
            descripcion: form.value.descripcion,
            precio: form.value.precio,
            capacidad_maxima: form.value.capacidad,
            activo: form.value.activo,
            evento: props.eventoId,
        };

        await eventosStore.updateZona(props.data.id, dataToSend);
        toastGlobalHelper.success("Zona actualizada exitosamente");
        emit("data_updated");
        closeModal();
    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            toastFormHelper.error(
                error.response.data.message || "Error al actualizar la zona"
            );
        } else {
            toastFormHelper.error("Error al actualizar la zona");
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
                <span>Editar Zona</span>
            </div>
        </template>

        <template #content>
            <ToastNotification ref="toastForm" />

            <form @submit.prevent="actualizarData" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="md:col-span-2">
                        <InputLabel for="nombre" value="Nombre de la Zona *" />
                        <InputText id="nombre" v-model="form.nombre" type="text" placeholder="Ej: VIP, Platea, General"
                            :error="errors.nombre" required />
                        <InputError :message="errors.nombre" />
                    </div>

                    <div class="md:col-span-2">
                        <InputLabel for="descripcion" value="Descripción" />
                        <InputTextarea id="descripcion" v-model="form.descripcion"
                            placeholder="Descripción de la zona..." rows="2" />
                        <InputError :message="errors.descripcion" />
                    </div>

                    <div>
                        <InputLabel for="precio" value="Precio (S/) *" />
                        <InputText id="precio" v-model="form.precio" type="number" step="0.01" min="0"
                            placeholder="0.00" :error="errors.precio" required />
                        <InputError :message="errors.precio" />
                    </div>

                    <div>
                        <InputLabel for="capacidad" value="Capacidad *" />
                        <InputText id="capacidad" v-model="form.capacidad" type="number" min="1"
                            placeholder="Número de tickets disponibles" :error="errors.capacidad" required />
                        <InputError :message="errors.capacidad" />
                    </div>

                    <div class="md:col-span-2">
                        <div class="flex items-center space-x-2 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                            <input id="activo" v-model="form.activo" type="checkbox"
                                class="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500 focus:ring-2" />
                            <label for="activo" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
                                Zona activa y disponible para venta
                            </label>
                        </div>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                            Las zonas inactivas no estarán disponibles para la compra de tickets
                        </p>
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
                    <span v-else>Actualizar Zona</span>
                </ButtonSave>
            </div>
        </template>
    </DialogModal>
</template>
