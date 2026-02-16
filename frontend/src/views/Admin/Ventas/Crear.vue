<script setup>
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import AdmLayout from "@/Layouts/AdmLayout.vue";
import FormularioVenta from "./Partes/FormularioVenta.vue";
import VoucherPreview from "./Partes/VoucherPreview.vue";
import { ChevronLeft } from "lucide-vue-next";

const router = useRouter();
const formData = ref(null);
const isFormValid = ref(false);

const handleFormUpdate = (data) => {
    formData.value = data;
};

const handleValidationUpdate = (valid) => {
    isFormValid.value = valid;
};

const handleSuccess = () => {
    router.push("/admin/ventas");
};

const volver = () => {
    router.push("/admin/ventas");
};
</script>

<template>
    <AdmLayout>
        <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
            <!-- Header -->
            <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div class="px-4 sm:px-6 lg:px-8 py-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-4">
                            <button @click="volver"
                                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                                <ChevronLeft class="w-5 h-5" />
                            </button>
                            <div>
                                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                                    Nueva venta de tickets
                                </h1>
                                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                    Complete los datos del cliente y seleccione los tickets
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Layout de 2 columnas -->
            <div class="py-6">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Columna Izquierda: Formulario (2/3) -->
                    <div class="lg:col-span-2">
                        <FormularioVenta @update:form-data="handleFormUpdate"
                            @update:validation="handleValidationUpdate" @success="handleSuccess" />
                    </div>

                    <!-- Columna Derecha: Preview (1/3) -->
                    <div class="lg:col-span-1">
                        <div class="sticky top-6">
                            <VoucherPreview :form-data="formData" :is-valid="isFormValid" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AdmLayout>
</template>
