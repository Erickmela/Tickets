<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEventosStore } from '@/stores/eventos';
import { useToasts } from '@/Helpers/useToasts';
import AdmLayout from '@/Layouts/AdmLayout.vue';
import VerticalSteeper from '@/components/VerticalSteeper.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import InputLabel from '@/components/Inputs/InputLabel.vue';
import InputText from '@/components/Inputs/InputText.vue';
import InputError from '@/components/Inputs/InputError.vue';
import ImageUpload from '@/components/Inputs/ImageUpload.vue';
import { ArrowLeft, Calendar, Image, MapPin } from 'lucide-vue-next';

const router = useRouter();
const eventosStore = useEventosStore();

const toast = ref(null);
const toastHelper = useToasts(toast);

const isSubmitting = ref(false);
const errors = ref({});

// Formulario dividido en pasos
const formBasico = ref({
    nombre: '',
    descripcion: '',
    fecha: '',
    hora_inicio: '',
    lugar: '',
    estado: '1' // Por defecto: Próximo
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

const steps = ['Información Básica', 'Imágenes', 'Zonas'];

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
            toastHelper.error('Debe agregar al menos una zona');
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

        // Imágenes (solo si son Files válidos)
        Object.keys(formImagenes.value).forEach(key => {
            const imagen = formImagenes.value[key];
            if (imagen && imagen instanceof File) {
                formData.append(key, imagen);
            }
        });

        // Zonas (como JSON string ya que FormData no soporta arrays anidados)
        formData.append('zonas_data', JSON.stringify(formZonas.value.zonas));

        await eventosStore.createEvento(formData);

        toastHelper.success('Evento creado exitosamente');
        setTimeout(() => {
            router.push({ name: 'admin-eventos' });
        }, 1500);

    } catch (error) {
        if (error.response?.data) {
            errors.value = error.response.data;
            const errorMsg = error.response.data.message || 'Error al crear el evento';
            toastHelper.error(errorMsg);
        } else {
            toastHelper.error('Error al crear el evento');
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

        <div class="py-6">
            <!-- Header -->
            <div class="mb-6">
                <button @click="volver" class="flex items-center gap-2 text-gray-600 hover:text-[#B3224D] mb-4">
                    <ArrowLeft class="w-5 h-5" />
                    Volver a Eventos
                </button>
            </div>

            <!-- Stepper -->
            <VerticalSteeper :steps="steps" :validate-step="validateStep" :is-submitting="isSubmitting"
                finish-button-text="Crear Evento" finish-submitting-text="Creando..." @finish="handleFinish">
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
                            Sube las imágenes promocionales del evento (todas son opcionales)
                        </p>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Imagen Principal -->
                            <ImageUpload v-model="formImagenes.imagen_principal" label="Imagen Principal (Portada)"
                                @remove="formImagenes.imagen_principal = null" />

                            <!-- Flyer -->
                            <ImageUpload v-model="formImagenes.imagen_flyer" label="Flyer Promocional"
                                @remove="formImagenes.imagen_flyer = null" />

                            <!-- Banner -->
                            <ImageUpload v-model="formImagenes.imagen_banner" label="Banner"
                                @remove="formImagenes.imagen_banner = null" />

                            <!-- Cartel -->
                            <ImageUpload v-model="formImagenes.imagen_cartel" label="Cartel / Póster"
                                @remove="formImagenes.imagen_cartel = null" />

                            <!-- Mapa de Zonas -->
                            <ImageUpload v-model="formImagenes.imagen_mapa_zonas" label="Mapa de Zonas"
                                @remove="formImagenes.imagen_mapa_zonas = null" />
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
                                    <h3 class="text-lg font-semibold text-gray-900">Zona {{ index + 1 }}</h3>
                                    <button @click="eliminarZona(index)" class="text-red-500 hover:text-red-700">
                                        Eliminar
                                    </button>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <!-- Nombre -->
                                    <div>
                                        <InputLabel :for="`zona_nombre_${index}`" value="Nombre *" />
                                        <InputText :id="`zona_nombre_${index}`" v-model="zona.nombre" type="text"
                                            placeholder="Ej: VIP, General, Palco" required
                                            @input="zona.nombre = zona.nombre.toUpperCase()"
                                            style="text-transform: uppercase;" />
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
