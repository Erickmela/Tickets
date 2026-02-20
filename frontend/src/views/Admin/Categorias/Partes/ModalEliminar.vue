<script setup>
import { ref, watch } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import DialogModal from "@/components/DialogModal.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputError from "@/components/Inputs/InputError.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useCategoriasStore } from "@/stores/categorias";
import { Folder, Tag, Package } from "lucide-vue-next";

const emit = defineEmits(["close", "data_destroyed"]);
const props = defineProps({ 
    show: Boolean, 
    data: Object 
});

const categoriasStore = useCategoriasStore();

function getFormData(data) {
    data = data ?? {};
    return {
        txt_eliminar: data.nombre ?? "",
        input_eliminar: "",
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
    form.value = getFormData(props.data);
    errors.value = {};
};

const eliminarData = async () => {
    errors.value = {};
    
    if (form.value.input_eliminar.trim() !== form.value.txt_eliminar.trim()) {
        errors.value = { input_eliminar: ['El valor ingresado no es correcto'] };
        return;
    }

    if (!props.data?.id) return;
    
    cargando.value = true;
    
    try {
        await categoriasStore.deleteCategoria(props.data.id);
        toastGlobalHelper.success("Categoría eliminada exitosamente");
        emit("data_destroyed");
        closeModal();
    } catch (error) {
        toastFormHelper.error(error.response?.data?.message || "Error al eliminar la categoría");
    } finally {
        cargando.value = false;
    }
};

watch(
    () => props.data,
    (nuevo) => {
        if (nuevo) {
            form.value = getFormData(nuevo);
        }
    },
    { immediate: true }
);
</script>

<template>
    <ToastNotification ref="toastGlobal" />
    <DialogModal :show="props.show" @close="closeModal" maxWidth="md">
        <template #title>
            <div class="flex items-center space-x-2 text-red-600">
                <svg 
                    class="w-6 h-6" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                >
                    <path 
                        stroke-linecap="round" 
                        stroke-linejoin="round" 
                        stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
                    />
                </svg>
                <span>Eliminar categoría</span>
            </div>
        </template>

        <template #content>
            <ToastNotification ref="toastForm" />
            <div class="mt-4 text-sm text-gray-600">
                <!-- Panel de información de la categoría -->
                <div class="py-8 border-y border-gray-100 dark:border-gray-700">
                    <div class="flex items-center justify-center text-gray-600 dark:text-white">
                        <Folder class="w-6 h-6 mr-2 text-gray-600 dark:text-gray-300" />
                        <p class="font-bold block text-lg">{{ data?.nombre ?? '' }}</p>
                    </div>
                </div>

                <!-- Formulario de confirmación -->
                <form class="mt-5" @submit.prevent="eliminarData">
                    <div>
                        <InputLabel for="input_eliminar" required>
                            Para confirmar, escriba "<span class="select-all rounded cursor-pointer font-mono bg-gray-100 dark:bg-gray-700 px-1 py-0.5">
                                {{ form?.txt_eliminar ?? "" }}
                            </span>" en el cuadro
                        </InputLabel>
                        <InputText 
                            v-model="form.input_eliminar" 
                            id="input_eliminar" 
                            class="mt-1 block w-full"
                            autocomplete="off"
                            :placeholder="`Escribe: ${form?.txt_eliminar}`"
                        />
                        <InputError :message="errors.input_eliminar?.[0]" />
                    </div>
                </form>
            </div>
        </template>

        <template #footer>
            <ButtonCancel @click="closeModal" :disabled="cargando">
                Cancelar
            </ButtonCancel>
            <ButtonSave 
                :disabled="cargando" 
                :class="{ 'opacity-25': cargando }" 
                @click="eliminarData" 
                class="ms-3 !bg-red-600 hover:!bg-red-700 focus:!ring-red-500"
            >
                {{ cargando ? "Eliminando..." : "Eliminar categoría" }}
            </ButtonSave>
        </template>
    </DialogModal>
</template>