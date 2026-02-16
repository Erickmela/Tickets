<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useEventosStore } from '@/stores/eventos';
import { useToasts } from '@/Helpers/useToasts';
import AdmLayout from '@/Layouts/AdmLayout.vue';
import VerticalSteeper from '@/components/VerticalSteeper.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import InputLabel from '@/components/Inputs/InputLabel.vue';
import InputText from '@/components/Inputs/InputText.vue';
import InputError from '@/components/Inputs/InputError.vue'; import ImageUpload from '@/components/Inputs/ImageUpload.vue'; import Loading from '@/components/Loading.vue';
import { ArrowLeft, Calendar, Image, MapPin } from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const eventosStore = useEventosStore();

const toast = ref(null);
const toastHelper = useToasts(toast);

const isSubmitting = ref(false);
const isLoading = ref(true);
const errors = ref({});

// Leer el slug que puede ser un encoded_id o un id normal
const eventoId = computed(() => route.params.slug);

// Opciones de categoría
const categorias = [
    'Música',
    'Deportes',
    'Teatro',
    'Conferencias',
    'Festivales',
    'Gastronomía',
    'Infantiles',
    'Otros'
];

// Opciones de región
const regiones = [
    'Lima', 'Arequipa', 'Cusco', 'La Libertad', 'Piura', 'Lambayeque',
    'Junín', 'Puno', 'Ica', 'Áncash', 'Cajamarca', 'Loreto',
    'San Martín', 'Ucayali', 'Huánuco', 'Ayacucho', 'Tacna', 'Moquegua',
    'Amazonas', 'Apurímac', 'Huancavelica', 'Madre de Dios', 'Pasco', 'Tumbes', 'Callao'
];

// Formulario dividido en pasos
const formBasico = ref({
    nombre: '',
    descripcion: '',
    categoria: 'Otros',
    fecha: '',
    hora_inicio: '',
    lugar: '',
    region: 'Lima',
    estado: '1'
});

const formImagenes = ref({
    imagen_principal: null,
    imagen_flyer: null,
    imagen_banner: null,
    imagen_cartel: null,
    imagen_mapa_zonas: null
});

const formZonas = ref({
    zonas: []
});

// URLs de imágenes existentes
const imagenesExistentes = ref({
    imagen_principal: null,
    imagen_flyer: null,
    imagen_banner: null,
    imagen_cartel: null,
    imagen_mapa_zonas: null
});

const steps = ['Información Básica', 'Imágenes', 'Zonas'];

// Cargar datos del evento
const cargarEvento = async () => {
    try {
        isLoading.value = true;
        const evento = await eventosStore.fetchEvento(eventoId.value);

        // Cargar datos básicos
        formBasico.value = {
            nombre: evento.nombre || '',
            descripcion: evento.descripcion || '',
            categoria: evento.categoria || 'Otros',
            fecha: evento.fecha || '',
            hora_inicio: evento.hora_inicio || '',
            lugar: evento.lugar || '',
            region: evento.region || 'Lima',
            estado: evento.estado || '1'
        };

        // Cargar URLs de imágenes existentes
        imagenesExistentes.value = {
            imagen_principal: evento.imagen_principal || null,
            imagen_flyer: evento.imagen_flyer || null,
            imagen_banner: evento.imagen_banner || null,
            imagen_cartel: evento.imagen_cartel || null,
            imagen_mapa_zonas: evento.imagen_mapa_zonas || null
        };

        // Cargar zonas
        if (evento.zonas && evento.zonas.length > 0) {
            formZonas.value.zonas = evento.zonas.map(zona => ({
                id: zona.id,
                nombre: zona.nombre || '',
                descripcion: zona.descripcion || '',
                precio: zona.precio || '',
                capacidad_maxima: zona.capacidad_maxima || '',
                activo: zona.activo !== undefined ? zona.activo : true
            }));
        }

    } catch (error) {
        toastHelper.error('Error al cargar el evento');
        router.push({ name: 'admin-eventos' });
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    cargarEvento();
});

// Validación por paso
const validateStep = async (stepIndex) => {
    errors.value = {};

    if (stepIndex === 0) {
        // Validar info básica
        if (!formBasico.value.nombre) {
            errors.value.nombre = 'El nombre es requerido';
            toastHelper.error('Complete todos los campos requeridos');
            return false;
        }
        if (!formBasico.value.fecha) {
            errors.value.fecha = 'La fecha es requerida';
            toastHelper.error('Complete todos los campos requeridos');
            return false;
        }
        if (!formBasico.value.lugar) {
            errors.value.lugar = 'El lugar es requerido';
            toastHelper.error('Complete todos los campos requeridos');
            return false;
        }
    }

    if (stepIndex === 2) {
        // Validar que haya al menos una zona
        if (formZonas.value.zonas.length === 0) {
            toastHelper.error('Debe tener al menos una zona');
            return false;
        }
    }

    return true;
};

// Manejo de zonas
const agregarZona = () => {
    formZonas.value.zonas.push({
        nombre: '',
        descripcion: '',
        precio: '',
        capacidad_maxima: '',
        activo: true
    });
};

const eliminarZona = (index) => {
    formZonas.value.zonas.splice(index, 1);
};

// Enviar formulario
const handleFinish = async () => {
    const isValid = await validateStep(2);
    if (!isValid) return;

    isSubmitting.value = true;
    errors.value = {};

    try {
        const formData = new FormData();

        // Datos básicos
        formData.append('nombre', formBasico.value.nombre);
        formData.append('descripcion', formBasico.value.descripcion || '');
        formData.append('fecha', formBasico.value.fecha);
        if (formBasico.value.hora_inicio && formBasico.value.hora_inicio.trim() !== '') {
            formData.append('hora_inicio', formBasico.value.hora_inicio);
        }
        formData.append('lugar', formBasico.value.lugar);
        formData.append('estado', formBasico.value.estado);
        formData.append('categoria', formBasico.value.categoria);
        formData.append('region', formBasico.value.region);

        // Imágenes (solo las nuevas)
        Object.keys(formImagenes.value).forEach(key => {
            if (formImagenes.value[key]) {
                formData.append(key, formImagenes.value[key]);
            }
        });

        // Zonas (como JSON string)
        formData.append('zonas_data', JSON.stringify(formZonas.value.zonas));

        await eventosStore.updateEvento(eventoId.value, formData);

        toastHelper.success('Evento actualizado exitosamente');
        setTimeout(() => {
            router.push({ name: 'admin-eventos' });
        }, 1500);

    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            const errorMsg = error.response.data.message || 'Error al actualizar el evento';
            toastHelper.error(errorMsg);
        } else {
            toastHelper.error('Error al actualizar el evento');
        }
    } finally {
        isSubmitting.value = false;
    }
};

const volver = () => {
    router.push({ name: 'admin-eventos' });
};
</script>

<template>
    <AdmLayout>
        <ToastNotification ref="toast" />

        <div v-if="isLoading" class="flex items-center justify-center min-h-screen">
            <Loading />
        </div>

        <div v-else class="py-6">
            <!-- Header -->
            <div class="mb-6">
                <button @click="volver" class="flex items-center gap-2 text-gray-600 hover:text-[#B3224D] mb-4">
                    <ArrowLeft class="w-5 h-5" />
                    Volver a Eventos
                </button>
            </div>

            <!-- Stepper -->
            <VerticalSteeper :steps="steps" :validate-step="validateStep" :is-submitting="isSubmitting"
                finish-button-text="Actualizar Evento" finish-submitting-text="Actualizando..." @finish="handleFinish">
                <!-- Step 0: Información Básica -->
                <template #step-0>
                    <div class="space-y-6">
                        <div class="flex items-center gap-3 mb-6">
                            <Calendar class="w-6 h-6 text-[#B3224D]" />
                            <h2 class="text-2xl font-bold text-gray-900">Información Básica</h2>
                        </div>

                        <!-- Nombre -->
                        <div>
                            <InputLabel for="nombre" value="Nombre del Evento *" />
                            <InputText id="nombre" v-model="formBasico.nombre" type="text"
                                placeholder="Ej: Fiesta de Año Nuevo 2026" required :error="errors.nombre" />
                            <InputError :message="errors.nombre" />
                        </div>

                        <!-- Descripción -->
                        <div>
                            <InputLabel for="descripcion" value="Descripción" />
                            <textarea id="descripcion" v-model="formBasico.descripcion" rows="4"
                                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                placeholder="Describe el evento..."></textarea>
                        </div>

                        <!-- Categoría y Región -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <InputLabel for="categoria" value="Categoría *" />
                                <select id="categoria" v-model="formBasico.categoria"
                                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                                    <option v-for="cat in categorias" :key="cat" :value="cat">{{ cat }}</option>
                                </select>
                            </div>

                            <div>
                                <InputLabel for="region" value="Región *" />
                                <select id="region" v-model="formBasico.region"
                                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                                    <option v-for="reg in regiones" :key="reg" :value="reg">{{ reg }}</option>
                                </select>
                            </div>
                        </div>

                        <!-- Fecha y Hora -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <InputLabel for="fecha" value="Fecha *" />
                                <InputText id="fecha" v-model="formBasico.fecha" type="date" required
                                    :error="errors.fecha" />
                                <InputError :message="errors.fecha" />
                            </div>

                            <div>
                                <InputLabel for="hora_inicio" value="Hora de Inicio" />
                                <InputText id="hora_inicio" v-model="formBasico.hora_inicio" type="time" />
                            </div>
                        </div>

                        <!-- Lugar -->
                        <div>
                            <InputLabel for="lugar" value="Lugar *" />
                            <InputText id="lugar" v-model="formBasico.lugar" type="text"
                                placeholder="Ej: Club Social Jala Jala" required :error="errors.lugar" />
                            <InputError :message="errors.lugar" />
                        </div>

                        <!-- Estado -->
                        <div>
                            <InputLabel for="estado" value="Estado" />
                            <select id="estado" v-model="formBasico.estado"
                                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                                <option value="1">Próximo</option>
                                <option value="2">Activo</option>
                                <option value="3">Finalizado</option>
                            </select>
                        </div>
                    </div>
                </template>

                <!-- Step 1: Imágenes -->
                <template #step-1>
                    <div class="space-y-6">
                        <div class="flex items-center gap-3 mb-6">
                            <Image class="w-6 h-6 text-[#B3224D]" />
                            <h2 class="text-2xl font-bold text-gray-900">Imágenes del Evento</h2>
                        </div>

                        <p class="text-sm text-gray-600 mb-4">
                            Actualiza las imágenes promocionales del evento (todas son opcionales)
                        </p>

                        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
                            <p class="text-sm text-blue-800 dark:text-blue-300">
                                <span class="font-semibold">💡 Recomendación de portada:</span> Para que la imagen principal se vea correctamente en el carrusel, usa dimensiones de <strong>1920x800 px</strong> (ratio 2.4:1). Formatos: JPG o PNG, peso máximo 500KB.
                            </p>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Imagen Principal -->
                            <ImageUpload v-model="formImagenes.imagen_principal"
                                :preview-url="imagenesExistentes.imagen_principal" label="Imagen Principal (Portada)"
                                @remove="() => { formImagenes.imagen_principal = null; imagenesExistentes.imagen_principal = null; }" />

                            <!-- Flyer -->
                            <ImageUpload v-model="formImagenes.imagen_flyer"
                                :preview-url="imagenesExistentes.imagen_flyer" label="Flyer Promocional"
                                @remove="() => { formImagenes.imagen_flyer = null; imagenesExistentes.imagen_flyer = null; }" />

                            <!-- Banner -->
                            <ImageUpload v-model="formImagenes.imagen_banner"
                                :preview-url="imagenesExistentes.imagen_banner" label="Banner"
                                @remove="() => { formImagenes.imagen_banner = null; imagenesExistentes.imagen_banner = null; }" />

                            <!-- Cartel -->
                            <ImageUpload v-model="formImagenes.imagen_cartel"
                                :preview-url="imagenesExistentes.imagen_cartel" label="Cartel / Póster"
                                @remove="() => { formImagenes.imagen_cartel = null; imagenesExistentes.imagen_cartel = null; }" />

                            <!-- Mapa de Zonas -->
                            <ImageUpload v-model="formImagenes.imagen_mapa_zonas"
                                :preview-url="imagenesExistentes.imagen_mapa_zonas" label="Mapa de Zonas"
                                @remove="() => { formImagenes.imagen_mapa_zonas = null; imagenesExistentes.imagen_mapa_zonas = null; }" />
                        </div>
                    </div>
                </template>

                <!-- Step 2: Zonas -->
                <template #step-2>
                    <div class="space-y-6">
                        <div class="flex items-center justify-between mb-6">
                            <div class="flex items-center gap-3">
                                <MapPin class="w-6 h-6 text-[#B3224D]" />
                                <h2 class="text-2xl font-bold text-gray-900">Zonas del Evento</h2>
                            </div>
                            <button @click="agregarZona"
                                class="px-4 py-2 bg-[#B3224D] text-white rounded-lg hover:bg-[#8d1a3c]">
                                + Agregar Zona
                            </button>
                        </div>

                        <div v-if="formZonas.zonas.length === 0" class="text-center py-12 bg-gray-50 rounded-lg">
                            <MapPin class="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <p class="text-gray-600 mb-4">No hay zonas agregadas</p>
                            <button @click="agregarZona"
                                class="px-6 py-3 bg-[#B3224D] text-white rounded-lg hover:bg-[#8d1a3c]">
                                Agregar Primera Zona
                            </button>
                        </div>

                        <!-- Lista de zonas -->
                        <div v-else class="space-y-4">
                            <div v-for="(zona, index) in formZonas.zonas" :key="index"
                                class="border border-gray-300 rounded-lg p-6 bg-white">
                                <div class="flex items-center justify-between mb-4">
                                    <h3 class="text-lg font-semibold text-gray-900">
                                        Zona {{ index + 1 }}
                                    </h3>
                                    <button @click="eliminarZona(index)" class="text-red-500 hover:text-red-700">
                                        Eliminar
                                    </button>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <!-- Nombre -->
                                    <div>
                                        <InputLabel :for="`zona_nombre_${index}`" value="Nombre *" />
                                        <InputText :id="`zona_nombre_${index}`" v-model="zona.nombre" type="text"
                                            placeholder="Ej: VIP, General, Palco" required />
                                    </div>

                                    <!-- Precio -->
                                    <div>
                                        <InputLabel :for="`zona_precio_${index}`" value="Precio (S/) *" />
                                        <InputText :id="`zona_precio_${index}`" v-model="zona.precio" type="number"
                                            step="0.01" placeholder="0.00" required />
                                    </div>

                                    <!-- Capacidad -->
                                    <div>
                                        <InputLabel :for="`zona_capacidad_${index}`" value="Capacidad Máxima *" />
                                        <InputText :id="`zona_capacidad_${index}`" v-model="zona.capacidad_maxima"
                                            type="number" placeholder="100" required />
                                    </div>

                                    <!-- Estado -->
                                    <div class="flex items-center mt-6">
                                        <input :id="`zona_activo_${index}`" v-model="zona.activo" type="checkbox"
                                            class="w-4 h-4 text-[#B3224D] border-gray-300 rounded focus:ring-[#B3224D]" />
                                        <label :for="`zona_activo_${index}`" class="ml-2 text-sm text-gray-700">
                                            Zona activa
                                        </label>
                                    </div>

                                    <!-- Descripción (full width) -->
                                    <div class="md:col-span-2">
                                        <InputLabel :for="`zona_descripcion_${index}`" value="Descripción" />
                                        <textarea :id="`zona_descripcion_${index}`" v-model="zona.descripcion" rows="2"
                                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent"
                                            placeholder="Descripción de la zona..."></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </VerticalSteeper>
        </div>
    </AdmLayout>
</template>
