<script setup>
import { ref, watch } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputError from "@/components/Inputs/InputError.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/helpers/useToasts";
import { useVentasStore } from "@/stores/ventas";
import { dateTimeText, formatPrice } from "@/helpers/Main";

const emit = defineEmits(["close", "data_destroyed"]);
const props = defineProps({
    show: {
        type: Boolean,
        default: false,
    },
    data: {
        type: Object,
        default: () => ({}),
    },
});

const ventasStore = useVentasStore();

function getFormData(data) {
    data = data ?? {};
    return {
        txt_eliminar: `VENTA-${data.id}` ?? "",
        input_eliminar: "",
        motivo: "",
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

const eliminar = async () => {
    errors.value = {};

    if (form.value.input_eliminar.trim() !== form.value.txt_eliminar.trim()) {
        errors.value = {
            input_eliminar: ["El valor ingresado no es correcto"],
        };
        return;
    }

    if (!form.value.motivo.trim()) {
        errors.value = {
            motivo: ["El motivo es obligatorio"],
        };
        return;
    }

    try {
        cargando.value = true;
        await ventasStore.anularVenta(props.data.id, form.value.motivo);
        toastGlobalHelper.success('Venta anulada correctamente');
        emit("data_destroyed");
        closeModal();
    } catch (error) {
        toastFormHelper.error(error.response?.data?.error || 'Error al anular la venta');
    } finally {
        cargando.value = false;
    }
};

watch(
    () => props.data,
    (nuevo) => {
        form.value = getFormData(nuevo);
    },
    { immediate: true }
);
</script>

<template>
    <ToastNotification ref="toastGlobal" />
    <DialogModal :show="props.show" @close="closeModal">
        <template #title> Anular Venta </template>

        <template #content>
            <ToastNotification ref="toastForm" />
            <div class="mt-4 text-sm text-gray-600 dark:text-gray-300">
                <div class="py-6 border-y border-gray-100 dark:border-gray-700">
                    <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                        <div class="flex items-start">
                            <svg class="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor"
                                viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <div class="ml-3">
                                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                                    Advertencia: Esta acción no se puede deshacer
                                </h3>
                                <p class="mt-2 text-sm text-red-700 dark:text-red-300">
                                    Estás a punto de anular la venta <strong>#{{ data?.id }}</strong>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">Cliente</p>
                            <p class="font-medium text-gray-900 dark:text-white">{{ data?.cliente_nombre }}</p>
                        </div>
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">Total</p>
                            <p class="font-semibold text-gray-900 dark:text-white">{{ formatPrice(data?.total_pagado) }}
                            </p>
                        </div>
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">Tickets</p>
                            <p class="font-medium text-gray-900 dark:text-white">{{ data?.cantidad_tickets }} tickets
                            </p>
                        </div>
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">Fecha</p>
                            <p class="text-gray-900 dark:text-white">{{ dateTimeText(data?.fecha_venta) }}</p>
                        </div>
                    </div>
                </div>

                <form class="mt-5 space-y-4">
                    <div>
                        <InputLabel for="motivo" required>
                            Motivo de la anulación
                        </InputLabel>
                        <textarea v-model="form.motivo" id="motivo" rows="3"
                            class="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:border-primary-500 focus:ring-primary-500 rounded-md shadow-sm"
                            placeholder="Explica brevemente por qué se anula esta venta..."></textarea>
                        <InputError :message="errors.motivo?.[0]" />
                    </div>

                    <div>
                        <InputLabel for="input_eliminar" required>
                            Para confirmar, escriba "
                            <span class="select-all rounded cursor-pointer font-mono bg-gray-100 dark:bg-gray-700 px-1">
                                {{ form?.txt_eliminar ?? "" }}
                            </span>
                            " en el cuadro
                        </InputLabel>
                        <InputText v-model="form.input_eliminar" id="input_eliminar" class="mt-1 block w-full"
                            autocomplete="off" />
                        <InputError :message="errors.input_eliminar?.[0]" />
                    </div>
                </form>
            </div>
        </template>

        <template #footer>
            <ButtonCancel @click="closeModal">Cancelar</ButtonCancel>
            <button :disabled="cargando" :class="{ 'opacity-25': cargando }" @click="eliminar"
                class="ms-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed">
                {{ cargando ? "Anulando..." : "Anular Venta" }}
            </button>
        </template>
    </DialogModal>
</template>
