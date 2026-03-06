<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useEventosStore } from '@/stores/eventos';
import { categoriasService } from '@/services/categoriasService';
import { useToasts } from '@/Helpers/useToasts';
import AdmLayout from '@/Layouts/AdmLayout.vue';
import VerticalSteeper from '@/components/VerticalSteeper.vue';
import ToastNotification from '@/components/ToastNotification.vue';
import InputLabel from '@/components/Inputs/InputLabel.vue';
import InputText from '@/components/Inputs/InputText.vue';
import InputError from '@/components/Inputs/InputError.vue'; 
import ImageUpload from '@/components/Inputs/ImageUpload.vue'; 
import Loading from '@/components/Loading.vue';
import { ArrowLeft, Calendar, Image, MapPin } from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const eventosStore = useEventosStore();

const toast = ref(null);
const toastHelper = useToasts(toast);

const isSubmitting = ref(false);
const isLoading = ref(true);
const errors = ref({});

// Leer el slug del evento desde los parámetros de la ruta
const eventoId = computed(() => route.params.slug);

// Categorías cargadas dinámicamente
const categorias = ref([]);
const categoriasLoading = ref(false);

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
    categoria: null, // Ahora es el ID de la categoría
    lugar: '',
    region: 'Lima',
    estado: '1'
});

const formPresentaciones = ref({
    presentaciones: []
});

const formImagenes = ref({
    imagen_principal: null,
    imagen_flyer: null,
    imagen_banner: null,
    imagen_cartel: null,
    imagen_mapa_zonas: null
});

// URLs de imágenes existentes
const imagenesExistentes = ref({
    imagen_principal: null,
    imagen_flyer: null,
    imagen_banner: null,
    imagen_cartel: null,
    imagen_mapa_zonas: null
});

const steps = ['Información Básica', 'Presentaciones', 'Imágenes', 'Zonas'];

// Cargar categorías desde el API
const cargarCategorias = async () => {
    try {
        categoriasLoading.value = true;
        const data = await categoriasService.getCategoriasSelect();
        
        if (Array.isArray(data)) {
            categorias.value = data;
        }
    } catch (error) {
        console.error('Error al cargar categorías:', error);
        toastHelper.error('Error al cargar las categorías');
    } finally {
        categoriasLoading.value = false;
    }
};

// Cargar datos del evento
const cargarEvento = async () => {
    try {
        isLoading.value = true;
        const evento = await eventosStore.fetchEvento(eventoId.value);

        // Cargar datos básicos (sin fecha/hora - ahora están en presentaciones)
        formBasico.value = {
            nombre: evento.nombre || '',
            descripcion: evento.descripcion || '',
            categoria: evento.categoria || null,
            lugar: evento.lugar || '',
            region: evento.region || 'Lima',
            estado: evento.estado || '1'
        };

        // Cargar presentaciones con sus zonas
        if (evento.presentaciones && evento.presentaciones.length > 0) {
            formPresentaciones.value.presentaciones = evento.presentaciones.map(present => ({
                id: present.id,
                fecha: present.fecha || '',
                hora_inicio: present.hora_inicio || '',
                descripcion: present.descripcion || '',
                zonas: present.zonas ? present.zonas.map(zona => ({
                    id: zona.id,
                    nombre: zona.nombre || '',
                    descripcion: zona.descripcion || '',
                    precio: zona.precio || '',
                    capacidad_maxima: zona.capacidad_maxima || '',
                    activo: zona.activo !== undefined ? zona.activo : true
                })) : []
            }));
        }

        // Cargar URLs de imágenes existentes
        imagenesExistentes.value = {
            imagen_principal: evento.imagen_principal || null,
            imagen_flyer: evento.imagen_flyer || null,
            imagen_banner: evento.imagen_banner || null,
            imagen_cartel: evento.imagen_cartel || null,
            imagen_mapa_zonas: evento.imagen_mapa_zonas || null
        };

    } catch (error) {
        toastHelper.error('Error al cargar el evento');
        router.push({ name: 'admin-eventos' });
    } finally {
        isLoading.value = false;
    }
};

onMounted(async () => {
    await cargarCategorias();
    await cargarEvento();
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
        if (!formBasico.value.categoria) {
            errors.value.categoria = 'La categoría es requerida';
            toastHelper.error('Complete todos los campos requeridos');
            return false;
        }
        if (!formBasico.value.lugar) {
            errors.value.lugar = 'El lugar es requerido';
            toastHelper.error('Complete todos los campos requeridos');
            return false;
        }
    }

    if (stepIndex === 1) {
        // Validar presentaciones
        if (formPresentaciones.value.presentaciones.length === 0) {
            toastHelper.error('Debe tener al menos una presentación');
            return false;
        }
        
        // Validar que cada presentación tenga fecha y hora
        for (let i = 0; i < formPresentaciones.value.presentaciones.length; i++) {
            const present = formPresentaciones.value.presentaciones[i];
            if (!present.fecha || !present.hora_inicio) {
                toastHelper.error(`La presentación ${i + 1} debe tener fecha y hora`);
                return false;
            }
        }
    }

    if (stepIndex === 3) {
        // Validar que haya al menos una zona en alguna presentación
        let tieneZonas = false;
        for (const present of formPresentaciones.value.presentaciones) {
            if (present.zonas && present.zonas.length > 0) {
                tieneZonas = true;
                break;
            }
        }
        if (!tieneZonas) {
            toastHelper.error('Debe tener al menos una zona en alguna presentación');
            return false;
        }
    }

    return true;
};

// Manejo de presentaciones
const agregarPresentacion = () => {
    formPresentaciones.value.presentaciones.push({
        fecha: '',
        hora_inicio: '',
        descripcion: '',
        zonas: []
    });
};

const eliminarPresentacion = (index) => {
    formPresentaciones.value.presentaciones.splice(index, 1);
};

// Manejo de zonas por presentación
const agregarZona = (presentIndex) => {
    formPresentaciones.value.presentaciones[presentIndex].zonas.push({
        nombre: '',
        descripcion: '',
        precio: '',
        capacidad_maxima: '',
        activo: true
    });
};

const eliminarZona = (presentIndex, zonaIndex) => {
    formPresentaciones.value.presentaciones[presentIndex].zonas.splice(zonaIndex, 1);
};

// Enviar formulario
const handleFinish = async () => {
    const isValid = await validateStep(3);
    if (!isValid) return;

    isSubmitting.value = true;
    errors.value = {};

    try {
        const formData = new FormData();

        // Datos básicos (sin fecha/hora_inicio - ahora están en presentaciones)
        formData.append('nombre', formBasico.value.nombre);
        formData.append('descripcion', formBasico.value.descripcion || '');
        formData.append('categoria', formBasico.value.categoria);
        formData.append('lugar', formBasico.value.lugar);
        formData.append('region', formBasico.value.region);
        formData.append('estado', formBasico.value.estado);

        // Imágenes (solo las nuevas)
        Object.keys(formImagenes.value).forEach(key => {
            if (formImagenes.value[key]) {
                formData.append(key, formImagenes.value[key]);
            }
        });

        // Presentaciones con sus zonas (nuevo formato)
        formData.append('presentaciones_data', JSON.stringify(formPresentaciones.value.presentaciones));

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
                                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    :disabled="categoriasLoading">
                                    <option value="" disabled>{{ categoriasLoading ? 'Cargando...' : 'Seleccione una categoría' }}</option>
                                    <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
                                </select>
                                <InputError :message="errors.categoria" />
                            </div>

                            <div>
                                <InputLabel for="region" value="Región *" />
                                <select id="region" v-model="formBasico.region"
                                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                                    <option v-for="reg in regiones" :key="reg" :value="reg">{{ reg }}</option>
                                </select>
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

                <!-- Step 1: Presentaciones -->
                <template #step-1>
                    <div class="space-y-6">
                        <div class="flex items-center justify-between mb-6">
                            <div class="flex items-center gap-3">
                                <Calendar class="w-6 h-6 text-[#B3224D]" />
                                <h2 class="text-2xl font-bold text-gray-900">Presentaciones del Evento</h2>
                            </div>
                            <button @click="agregarPresentacion"
                                class="px-4 py-2 bg-[#B3224D] text-white rounded-lg hover:bg-[#8d1a3c]">
                                + Agregar Presentación
                            </button>
                        </div>

                        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
                            <p class="text-sm text-blue-800 dark:text-blue-300">
                                <span class="font-semibold">¿Qué son las presentaciones?</span> Son las diferentes fechas y horarios en los que se realizará el evento. Por ejemplo, un concierto puede tener presentaciones el viernes y sábado.
                            </p>
                        </div>

                        <div v-if="formPresentaciones.presentaciones.length === 0" class="text-center py-12 bg-gray-50 rounded-lg">
                            <Calendar class="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <p class="text-gray-600 mb-4">No hay presentaciones agregadas</p>
                            <button @click="agregarPresentacion"
                                class="px-6 py-3 bg-[#B3224D] text-white rounded-lg hover:bg-[#8d1a3c]">
                                Agregar Primera Presentación
                            </button>
                       </div>

                        <!-- Lista de presentaciones -->
                        <div v-else class="space-y-4">
                            <div v-for="(present, index) in formPresentaciones.presentaciones" :key="index"
                                class="border border-gray-300 rounded-lg p-6 bg-white">
                                <div class="flex items-center justify-between mb-4">
                                    <h3 class="text-lg font-semibold text-gray-900">Presentación {{ index + 1 }}</h3>
                                    <button @click="eliminarPresentacion(index)" class="text-red-500 hover:text-red-700">
                                        Eliminar
                                    </button>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <!-- Fecha -->
                                    <div>
                                        <InputLabel :for="`present_fecha_${index}`" value="Fecha *" />
                                        <InputText :id="`present_fecha_${index}`" v-model="present.fecha" type="date" required />
                                    </div>

                                    <!-- Hora -->
                                    <div>
                                        <InputLabel :for="`present_hora_${index}`" value="Hora de Inicio *" />
                                        <InputText :id="`present_hora_${index}`" v-model="present.hora_inicio" type="time" required />
                                    </div>

                                    <!-- Descripción -->
                                    <div>
                                        <InputLabel :for="`present_desc_${index}`" value="Descripción" />
                                        <InputText :id="`present_desc_${index}`" v-model="present.descripcion" type="text" 
                                            placeholder="Ej: Noche 1, Matinée..." />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>

                <!-- Step 2: Imágenes -->
                <template #step-2>
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

                <!-- Step 3: Zonas por Presentación -->
                <template #step-3>
                    <div class="space-y-6">
                        <div class="flex items-center gap-3 mb-6">
                            <MapPin class="w-6 h-6 text-[#B3224D]" />
                            <h2 class="text-2xl font-bold text-gray-900">Zonas del Evento</h2>
                        </div>

                        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
                            <p class="text-sm text-blue-800 dark:text-blue-300">
                                <span class="font-semibold">Importante:</span> Configura las zonas (VIP, General, etc.) para cada presentación. Puedes tener diferentes zonas o precios según la fecha.
                            </p>
                        </div>

                        <div v-if="formPresentaciones.presentaciones.length === 0" class="text-center py-12 bg-gray-50 rounded-lg">
                            <p class="text-gray-600">Primero debe agregar al menos una presentación en el paso anterior</p>
                        </div>

                        <!-- Zonas por cada presentación -->
                        <div v-else class="space-y-6">
                            <div v-for="(present, presentIndex) in formPresentaciones.presentaciones" :key="presentIndex"
                                class="border-2 border-[#B3224D] rounded-lg p-6 bg-white">
                                <!-- Header de presentación -->
                                <div class="flex items-center justify-between mb-4 pb-4 border-b">
                                    <div>
                                        <h3 class="text-lg font-bold text-gray-900">
                                            Presentación {{ presentIndex + 1 }}
                                            <span v-if="present.descripcion" class="text-sm font-normal text-gray-600">
                                                - {{ present.descripcion }}
                                            </span>
                                        </h3>
                                        <p class="text-sm text-gray-600 mt-1">
                                            {{ present.fecha }} {{ present.hora_inicio ? `a las ${present.hora_inicio}` : '' }}
                                        </p>
                                    </div>
                                    <button @click="agregarZona(presentIndex)"
                                        class="px-3 py-1.5 text-sm bg-[#B3224D] text-white rounded hover:bg-[#8d1a3c]">
                                        + Zona
                                    </button>
                                </div>

                                <!-- Zonas de esta presentación -->
                                <div v-if="!present.zonas || present.zonas.length === 0" 
                                    class="text-center py-8 bg-gray-50 rounded-lg">
                                    <p class="text-gray-600 text-sm mb-3">No hay zonas para esta presentación</p>
                                    <button @click="agregarZona(presentIndex)"
                                        class="px-4 py-2 bg-[#B3224D] text-white rounded hover:bg-[#8d1a3c]">
                                        Agregar Primera Zona
                                    </button>
                                </div>

                                <div v-else class="space-y-4">
                                    <div v-for="(zona, zonaIndex) in present.zonas" :key="zonaIndex"
                                        class="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                        <div class="flex items-center justify-between mb-3">
                                            <h4 class="font-semibold text-gray-800">Zona {{ zonaIndex + 1 }}</h4>
                                            <button @click="eliminarZona(presentIndex, zonaIndex)" 
                                                class="text-red-500 hover:text-red-700 text-sm">
                                                Eliminar
                                            </button>
                                        </div>

                                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                            <!-- Nombre -->
                                            <div>
                                                <InputLabel :for="`zona_${presentIndex}_${zonaIndex}_nombre`" 
                                                    value="Nombre *" class="text-sm" />
                                                <InputText :id="`zona_${presentIndex}_${zonaIndex}_nombre`" 
                                                    v-model="zona.nombre" type="text"
                                                    placeholder="Ej: VIP, GENERAL, PALCO" 
                                                    @input="zona.nombre = zona.nombre.toUpperCase()"
                                                    class="text-sm" />
                                            </div>

                                            <!-- Precio -->
                                            <div>
                                                <InputLabel :for="`zona_${presentIndex}_${zonaIndex}_precio`" 
                                                    value="Precio (S/) *" class="text-sm" />
                                                <InputText :id="`zona_${presentIndex}_${zonaIndex}_precio`" 
                                                    v-model="zona.precio" type="number"
                                                    step="0.01" placeholder="0.00" class="text-sm" />
                                            </div>

                                            <!-- Capacidad -->
                                            <div>
                                                <InputLabel :for="`zona_${presentIndex}_${zonaIndex}_capacidad`" 
                                                    value="Capacidad *" class="text-sm" />
                                                <InputText :id="`zona_${presentIndex}_${zonaIndex}_capacidad`" 
                                                    v-model="zona.capacidad_maxima"
                                                    type="number" placeholder="100" class="text-sm" />
                                            </div>

                                            <!-- Estado -->
                                            <div class="flex items-center mt-5">
                                                <input :id="`zona_${presentIndex}_${zonaIndex}_activo`" 
                                                    v-model="zona.activo" type="checkbox"
                                                    class="w-4 h-4 text-[#B3224D] border-gray-300 rounded focus:ring-[#B3224D]" />
                                                <label :for="`zona_${presentIndex}_${zonaIndex}_activo`" 
                                                    class="ml-2 text-sm text-gray-700">
                                                    Zona activa
                                                </label>
                                            </div>

                                            <!-- Descripción (full width) -->
                                            <div class="md:col-span-2">
                                                <InputLabel :for="`zona_${presentIndex}_${zonaIndex}_desc`" 
                                                    value="Descripción" class="text-sm" />
                                                <textarea :id="`zona_${presentIndex}_${zonaIndex}_desc`" 
                                                    v-model="zona.descripcion" rows="2"
                                                    class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#B3224D] focus:border-transparent"
                                                    placeholder="Descripción de la zona..."></textarea>
                                            </div>
                                        </div>
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