<script setup>
import { ref } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputTextarea from "@/components/Inputs/InputTextarea.vue";
import InputError from "@/components/Inputs/InputError.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/helpers/useToasts";
import { useEventosStore } from "@/stores/eventos";

const emit = defineEmits(["close", "data_created"]);
const props = defineProps({
    show: Boolean,
    eventoId: Number,
});

const eventosStore = useEventosStore();

function getFormData() {
    return {
        nombre: "",
        descripcion: "",
        precio: "",
        capacidad: "",
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
    if (!props.eventoId) {
        toastFormHelper.error("No se ha seleccionado un evento");
        return;
    }

    cargando.value = true;
    errors.value = {};

    try {
        const dataToSend = {
            nombre: form.value.nombre,
            descripcion: form.value.descripcion,
            precio: form.value.precio,
            capacidad_maxima: form.value.capacidad,
            evento: props.eventoId,
        };

        await eventosStore.createZona(dataToSend);
        toastGlobalHelper.success("Zona creada exitosamente");
        emit("data_created");
        closeModal();
    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            toastFormHelper.error(
                error.response.data.message || "Error al crear la zona"
            );
        } else {
            toastFormHelper.error("Error al crear la zona");
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
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <span>Crear Nueva Zona</span>
            </div>
        </template>

        <template #content>
            <ToastNotification ref="toastForm" />

            <form @submit.prevent="crearData" class="space-y-4">
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
                </div>
            </form>
        </template>

        <template #footer>
            <div class="flex justify-end space-x-2">
                <ButtonCancel @click="closeModal" :disabled="cargando">
                    Cancelar
                </ButtonCancel>
                <ButtonSave @click="crearData" :disabled="cargando">
                    <span v-if="cargando">Guardando...</span>
                    <span v-else>Guardar Zona</span>
                </ButtonSave>
            </div>
        </template>
    </DialogModal>
</template>
