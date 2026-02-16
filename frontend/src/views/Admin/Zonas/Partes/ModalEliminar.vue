<script setup>
import { ref } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/helpers/useToasts";
import { useEventosStore } from "@/stores/eventos";

const emit = defineEmits(["close", "data_destroyed"]);
const props = defineProps({
    show: Boolean,
    data: Object,
});

const eventosStore = useEventosStore();

const toastForm = ref(null);
const toastGlobal = ref(null);
const toastFormHelper = useToasts(toastForm);
const toastGlobalHelper = useToasts(toastGlobal);
const cargando = ref(false);

const closeModal = () => {
    emit("close");
};

const eliminarData = async () => {
    if (!props.data?.id) return;

    cargando.value = true;

    try {
        await eventosStore.deleteZona(props.data.id);
        toastGlobalHelper.success("Zona eliminada exitosamente");
        emit("data_destroyed");
        closeModal();
    } catch (error) {
        toastFormHelper.error(
            error.response?.data?.message || "Error al eliminar la zona"
        );
    } finally {
        cargando.value = false;
    }
};
</script>

<template>
    <DialogModal :show="show" @close="closeModal" max-width="md">
        <template #title>
            <div class="flex items-center space-x-2 text-red-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>Confirmar Eliminación</span>
            </div>
        </template>

        <template #content>
            <ToastNotification ref="toastForm" />

            <div class="space-y-4">
                <p class="text-gray-600 dark:text-gray-400">
                    ¿Estás seguro de que deseas eliminar esta zona?
                </p>

                <div v-if="data" class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div class="space-y-2">
                        <div>
                            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Zona:</span>
                            <p class="text-gray-900 dark:text-white font-semibold">{{ data.nombre }}</p>
                        </div>
                        <div v-if="data.precio">
                            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Precio:</span>
                            <p class="text-gray-900 dark:text-white">S/ {{ parseFloat(data.precio).toFixed(2) }}</p>
                        </div>
                        <div v-if="data.capacidad">
                            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Capacidad:</span>
                            <p class="text-gray-900 dark:text-white">{{ data.capacidad }} tickets</p>
                        </div>
                        <div v-if="data.tickets_vendidos">
                            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Tickets Vendidos:</span>
                            <p class="text-gray-900 dark:text-white">{{ data.tickets_vendidos }}</p>
                        </div>
                    </div>
                </div>

                <p class="text-sm text-red-600 dark:text-red-400 font-medium">
                    ⚠️ Esta acción no se puede deshacer. Se eliminarán también todos los tickets asociados.
                </p>
            </div>
        </template>

        <template #footer>
            <div class="flex justify-end space-x-2">
                <ButtonCancel @click="closeModal" :disabled="cargando">
                    Cancelar
                </ButtonCancel>
                <ButtonSave @click="eliminarData" :disabled="cargando" class="!bg-red-600 hover:!bg-red-700">
                    <span v-if="cargando">Eliminando...</span>
                    <span v-else>Eliminar Zona</span>
                </ButtonSave>
            </div>
        </template>
    </DialogModal>
</template>
