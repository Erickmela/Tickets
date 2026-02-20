<script setup>
import { ref, watch, computed } from "vue";
import { X, ImagePlus } from 'lucide-vue-next';

const props = defineProps({
    // v-model
    modelValue: { default: null },

    // Aspecto ej. 16:9
    aspectRatioNumerator: { type: Number, default: null },
    aspectRatioDenominator: { type: Number, default: null },

    // Peso máximo en MB
    maxSizeMb: { type: Number, default: 2 },

    accept: {
        type: Array,
        default: () => ["image/jpeg", "image/png", "image/webp"],
    },
    previewImage: { type: String, default: null },
});

const emit = defineEmits(["update:modelValue", "error", "cleared"]);
const preview = ref(null);

// Generar / limpiar preview
watch(
    () => props.modelValue,
    (file) => {
        if (!file) {
            preview.value = props.previewImage ?? null;
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => (preview.value = e.target.result);
        reader.readAsDataURL(file);
    },
    { immediate: true }
);

// Actualiza preview si cambia previewImage y no hay archivo
watch(
    () => props.previewImage,
    (val) => {
        if (!props.modelValue) {
            preview.value = val;
        }
    }
);

// Relación decimal para validación
const decimalRatio = computed(() => {
    if (!props.aspectRatioNumerator || !props.aspectRatioDenominator)
        return null;
    return props.aspectRatioNumerator / props.aspectRatioDenominator;
});

const onChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Tipo
    if (!props.accept.includes(file.type)) {
        return emit("error", [`Formato no válido. Solo ${props.accept.join(", ")}`]);
    }

    // Tamaño
    if (file.size > props.maxSizeMb * 1024 * 1024) {
        return emit("error", [`La imagen no debe exceder ${props.maxSizeMb} MB`]);
    }

    // Relación
    if (decimalRatio.value) {
        const ok = await validateAspect(file, decimalRatio.value);
        if (!ok) {
            return emit("error", [`La imagen debe tener relación ${props.aspectRatioNumerator}:${props.aspectRatioDenominator}`]);
        }
    }

    // OK
    emit("error", null);
    emit("update:modelValue", file);
};

// Helper para validar aspecto
function validateAspect(file, ratio) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const actual = img.width / img.height;
            resolve(Math.abs(actual - ratio) < 0.1);
        };
        img.src = URL.createObjectURL(file);
    });
}

// Eliminar
const remove = () => {
    emit("update:modelValue", null);
    emit("cleared");
    preview.value = null;
};
</script>

<template>
    <div>
        <!-- preview -->
        <div v-if="preview" class="relative mt-1 group">
            <img :src="preview" alt="Vista previa" class="object-cover w-full aspect-video bg-transparent rounded-md" />

            <!-- botón eliminar -->
            <button type="button" @click="remove"
                class="absolute top-2 right-2 p-1 bg-primary-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                <X class="w-5 h-5 text-white" />
            </button>
        </div>

        <!-- input file -->
        <div v-else
            class="mt-1 flex items-center justify-center w-full aspect-video border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg cursor-pointer transition-colors hover:border-primary-400 dark:hover:border-primary-400 dark:hover:bg-gray-700 hover:bg-gray-100">
            <label class="flex flex-col items-center justify-center w-full h-full cursor-pointer">
                <input type="file" class="hidden" :accept="accept.join(',')" @change="onChange" />

                <ImagePlus class="w-8 h-8 text-gray-400 dark:text-gray-500" />

                <p class="mt-2 text-sm text-gray-500">
                    <span class="font-medium text-primary-600">Haz clic para subir</span>
                    o arrastra una imagen
                </p>

                <p class="text-xs text-gray-400">
                    Relación
                    {{
                        props.aspectRatioNumerator &&
                            props.aspectRatioDenominator
                            ? `${props.aspectRatioNumerator}:${props.aspectRatioDenominator}`
                            : "libre"
                    }}
                    - Máx. {{ maxSizeMb }} MB
                </p>
            </label>
        </div>
    </div>
</template>
