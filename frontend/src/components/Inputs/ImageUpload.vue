<script setup>
import { ref, computed, watch } from 'vue';
import { Image as ImageIcon, X, Eye, Upload } from 'lucide-vue-next';
import DialogModal from '@/components/DialogModal.vue';

const props = defineProps({
    modelValue: {
        type: [File, String, null],
        default: null
    },
    label: {
        type: String,
        default: ''
    },
    previewUrl: {
        type: String,
        default: null
    },
    accept: {
        type: String,
        default: 'image/*'
    },
    maxSize: {
        type: Number,
        default: 5 // MB
    },
    required: {
        type: Boolean,
        default: false
    },
    error: {
        type: String,
        default: ''
    },
    disabled: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:modelValue', 'remove']);

const fileInput = ref(null);
const localPreview = ref(null);
const showImageModal = ref(false);
const errorMessage = ref('');

// Computed para determinar qué imagen mostrar
const imageToShow = computed(() => {
    if (localPreview.value) return localPreview.value;
    if (props.previewUrl) return props.previewUrl;
    return null;
});

const hasImage = computed(() => !!imageToShow.value);

// Manejar selección de archivo
const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    errorMessage.value = '';

    // Validar tipo
    if (!file.type.startsWith('image/')) {
        errorMessage.value = 'El archivo debe ser una imagen';
        return;
    }

    // Validar tamaño
    const fileSizeMB = file.size / 1024 / 1024;
    if (fileSizeMB > props.maxSize) {
        errorMessage.value = `La imagen no debe superar ${props.maxSize}MB`;
        return;
    }

    // Crear preview
    const reader = new FileReader();
    reader.onload = (e) => {
        localPreview.value = e.target.result;
    };
    reader.readAsDataURL(file);

    // Emitir el archivo
    emit('update:modelValue', file);
};

// Abrir selector de archivos
const openFileSelector = () => {
    if (!props.disabled) {
        fileInput.value?.click();
    }
};

// Eliminar imagen
const removeImage = () => {
    localPreview.value = null;
    if (fileInput.value) {
        fileInput.value.value = '';
    }
    emit('remove');
    emit('update:modelValue', null);
    errorMessage.value = '';
};

// Ver imagen completa
const viewFullImage = () => {
    if (hasImage.value) {
        showImageModal.value = true;
    }
};

// Limpiar preview local si se limpia externamente
watch(() => props.modelValue, (newValue) => {
    if (newValue === null) {
        localPreview.value = null;
    }
});

watch(() => props.previewUrl, (newValue) => {
    if (!newValue && !props.modelValue) {
        localPreview.value = null;
    }
});
</script>

<template>
    <div class="space-y-2">
        <!-- Label -->
        <label v-if="label" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {{ label }}
            <span v-if="required" class="text-red-500 ml-1">*</span>
        </label>

        <!-- Área de carga -->
        <div class="relative">
            <!-- Input oculto -->
            <input
                ref="fileInput"
                type="file"
                :accept="accept"
                @change="handleFileSelect"
                class="hidden"
                :disabled="disabled"
            />

            <!-- Preview o área de carga -->
            <div
                v-if="hasImage"
                class="relative group border-2 border-gray-300 rounded-lg overflow-hidden bg-gray-50"
            >
                <!-- Imagen preview -->
                <img
                    :src="imageToShow"
                    :alt="label"
                    class="w-full h-48 object-cover"
                />

                <!-- Overlay con acciones -->
                <div
                    class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100"
                >
                    <!-- Botón ver imagen completa -->
                    <button
                        type="button"
                        @click="viewFullImage"
                        class="p-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
                        title="Ver imagen completa"
                    >
                        <Eye class="w-5 h-5 text-gray-700" />
                    </button>

                    <!-- Botón cambiar imagen -->
                    <button
                        v-if="!disabled"
                        type="button"
                        @click="openFileSelector"
                        class="p-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
                        title="Cambiar imagen"
                    >
                        <Upload class="w-5 h-5 text-[#B3224D]" />
                    </button>

                    <!-- Botón eliminar -->
                    <button
                        v-if="!disabled"
                        type="button"
                        @click="removeImage"
                        class="p-2 bg-white rounded-lg hover:bg-red-50 transition-colors"
                        title="Eliminar imagen"
                    >
                        <X class="w-5 h-5 text-red-500" />
                    </button>
                </div>
            </div>

            <!-- Área de carga vacía -->
            <div
                v-else
                @click="openFileSelector"
                class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-[#B3224D] hover:bg-gray-50 transition-all"
                :class="{ 'cursor-not-allowed opacity-60': disabled }"
            >
                <ImageIcon class="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p class="text-sm text-gray-600 mb-1">
                    <span class="text-[#B3224D] font-semibold">Haz clic para subir</span>
                    o arrastra una imagen
                </p>
                <p class="text-xs text-gray-500">
                    PNG, JPG, JPEG (máx. {{ maxSize }}MB)
                </p>
            </div>
        </div>

        <!-- Error -->
        <p v-if="errorMessage || error" class="text-sm text-red-500">
            {{ errorMessage || error }}
        </p>

        <!-- Modal para ver imagen completa -->
        <DialogModal :show="showImageModal" @close="showImageModal = false" max-width="4xl">
            <template #title>
                <div class="flex items-center gap-2">
                    <ImageIcon class="w-5 h-5 text-[#B3224D]" />
                    {{ label || 'Imagen' }}
                </div>
            </template>

            <template #content>
                <div class="flex items-center justify-center bg-gray-100 rounded-lg p-4">
                    <img
                        :src="imageToShow"
                        :alt="label"
                        class="max-w-full max-h-[70vh] object-contain"
                    />
                </div>
            </template>

            <template #footer>
                <button
                    @click="showImageModal = false"
                    class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                    Cerrar
                </button>
            </template>
        </DialogModal>
    </div>
</template>
