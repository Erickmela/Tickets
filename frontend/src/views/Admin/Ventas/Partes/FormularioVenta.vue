<script setup>
import { ref, onMounted, watch, computed } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputSelect from "@/components/Inputs/InputSelect.vue";
import InputTextarea from "@/components/Inputs/InputTextarea.vue";
import InputError from "@/components/Inputs/InputError.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { manejarErrorAPI } from "@/Helpers/errorHandler";
import { useVentasStore } from "@/stores/ventas";
import { useEventosStore } from "@/stores/eventos";
import { Plus, Trash2, Search } from "lucide-vue-next";

const emit = defineEmits(["update:formData", "update:validation", "success"]);

const ventasStore = useVentasStore();
const eventosStore = useEventosStore();

function getFormData() {
    return {
        evento_id: "",
        cliente_dni: "",
        cliente_nombre: "",
        cliente_telefono: "",
        cliente_email: "",
        metodo_pago: "EFECTIVO",
        nro_operacion: "",
        observaciones: "",
        tickets: [
            {
                zona_id: "",
                dni_titular: "",
                nombre_titular: "",
            },
        ],
    };
}

const form = ref(getFormData());
const eventosActivos = ref([]);
const zonas = ref([]);
const eventoActivo = ref(null);
const buscandoCliente = ref(false);
const clienteEncontrado = ref(false);

const errors = ref({});
const toastForm = ref(null);
const toastFormHelper = useToasts(toastForm);
const cargando = ref(false);

// Computed: Validación del formulario
const isFormValid = computed(() => {
    return (
        form.value.evento_id !== "" &&
        eventoActivo.value !== null &&
        form.value.cliente_dni.length === 8 &&
        form.value.cliente_nombre.trim() !== "" &&
        form.value.tickets.length > 0 &&
        form.value.tickets.every(t => t.zona_id && t.dni_titular.length === 8 && t.nombre_titular.trim() !== "")
    );
});

// Computed: Total de la venta
const totalVenta = computed(() => {
    return form.value.tickets.reduce((total, ticket) => {
        const zona = zonas.value.find(z => z.id === parseInt(ticket.zona_id));
        return total + (zona ? parseFloat(zona.precio) : 0);
    }, 0);
});

// Watch: Emitir cambios del formulario
watch(form, (newForm) => {
    emit("update:formData", {
        ...newForm,
        total: totalVenta.value,
        zonas: zonas.value,
        evento: eventoActivo.value
    });
}, { deep: true });

// Watch: Emitir estado de validación
watch(isFormValid, (valid) => {
    emit("update:validation", valid);
});

// Watch: Emitir cambios cuando cambia el evento activo
watch(eventoActivo, () => {
    emit("update:formData", {
        ...form.value,
        total: totalVenta.value,
        zonas: zonas.value,
        evento: eventoActivo.value
    });
});

// Watch: Emitir cambios cuando cambian las zonas
watch(zonas, () => {
    emit("update:formData", {
        ...form.value,
        total: totalVenta.value,
        zonas: zonas.value,
        evento: eventoActivo.value
    });
}, { deep: true });

// Watch: Limpiar estado de cliente encontrado cuando cambia el DNI
watch(() => form.value.cliente_dni, (newDni) => {
    // Si el DNI cambia y no tiene 8 dígitos, limpiar el estado
    if (newDni.length !== 8) {
        clienteEncontrado.value = false;
    }
});

// Watch: Cargar zonas cuando se selecciona un evento
watch(() => form.value.evento_id, async (newEventoId, oldEventoId) => {
    if (newEventoId) {
        await cargarZonasEvento(newEventoId);
        
        // Si cambió el evento (no es la carga inicial), limpiar las zonas de los tickets
        if (oldEventoId && oldEventoId !== newEventoId) {
            form.value.tickets.forEach(ticket => {
                ticket.zona_id = "";
            });
        }
    } else {
        zonas.value = [];
        eventoActivo.value = null;
    }
});

// Función para cargar zonas de un evento específico
const cargarZonasEvento = async (eventoId) => {
    try {
        // Buscar el evento en la lista de eventos activos
        eventoActivo.value = eventosActivos.value.find(e => e.id === parseInt(eventoId));
        
        // Cargar las zonas del evento
        zonas.value = await eventosStore.fetchZonasDisponibles(eventoId);
        
        if (zonas.value.length === 0) {
            toastFormHelper.warning(
                'Sin zonas disponibles',
                'El evento seleccionado no tiene zonas con disponibilidad'
            );
        }
    } catch (error) {
        console.error('Error al cargar zonas:', error);
        toastFormHelper.error(
            'Error al cargar zonas',
            'No se pudieron cargar las zonas del evento seleccionado'
        );
        zonas.value = [];
    }
};

onMounted(async () => {
    try {
        // Cargar todos los eventos activos
        eventosActivos.value = await eventosStore.fetchEventosActivos();
        
        // Si solo hay un evento activo, seleccionarlo automáticamente
        if (eventosActivos.value.length === 1) {
            form.value.evento_id = eventosActivos.value[0].id;
        }
        
        // Emitir datos iniciales
        emit("update:formData", {
            ...form.value,
            total: totalVenta.value,
            zonas: zonas.value,
            evento: eventoActivo.value
        });
        emit("update:validation", isFormValid.value);
    } catch (error) {
        console.error('Error al cargar datos:', error);
        if (error.response?.status === 404) {
            toastFormHelper.error(
                'Sin eventos activos',
                'No hay eventos activos en este momento. Active un evento para poder vender.'
            );
        } else {
            toastFormHelper.error(
                'Error al cargar datos',
                'No se pudieron cargar los eventos activos'
            );
        }
    }
});

const agregarTicket = () => {
    if (form.value.tickets.length < 3) {
        form.value.tickets.push({
            zona_id: "",
            dni_titular: "",
            nombre_titular: "",
        });
    }
};

const eliminarTicket = (index) => {
    if (form.value.tickets.length > 1) {
        form.value.tickets.splice(index, 1);
    }
};

const buscarCliente = async () => {
    if (form.value.cliente_dni.length === 8) {
        buscandoCliente.value = true;
        clienteEncontrado.value = false;
        try {
            const cliente = await ventasStore.buscarClientePorDNI(form.value.cliente_dni);
            if (cliente) {
                form.value.cliente_nombre = cliente.nombre_completo;
                form.value.cliente_telefono = cliente.telefono || "";
                form.value.cliente_email = cliente.email || "";
                clienteEncontrado.value = true;
                toastFormHelper.success(
                    "Cliente encontrado",
                    `Se encontró el cliente ${cliente.nombre_completo}. Los datos se han autocompletado.`
                );
            }
        } catch (error) {
            // Cliente no encontrado, es nuevo
            clienteEncontrado.value = false;
            // Limpiar campos si es un DNI nuevo
            form.value.cliente_nombre = "";
            form.value.cliente_telefono = "";
            form.value.cliente_email = "";
            toastFormHelper.info(
                "Cliente nuevo",
                "No se encontró el DNI en el sistema. Complete los datos del nuevo cliente."
            );
        } finally {
            buscandoCliente.value = false;
        }
    }
};

const copiarDatosCliente = (index) => {
    form.value.tickets[index].dni_titular = form.value.cliente_dni;
    form.value.tickets[index].nombre_titular = form.value.cliente_nombre;
};

const crearVenta = async () => {
    cargando.value = true;
    errors.value = {};

    try {
        const data = await ventasStore.crearVenta(form.value);
        toastFormHelper.success(
            'Venta creada exitosamente',
            `Se creó la venta #${data.venta?.id || ''} con ${form.value.tickets.length} ticket(s)`
        );
        setTimeout(() => {
            emit("success");
        }, 1500);
    } catch (error) {
        const errorInfo = manejarErrorAPI(error, 'Error al crear la venta');
        
        if (errorInfo.tieneErroresValidacion) {
            errors.value = errorInfo.errores;
            toastFormHelper.error(
                'Error en el formulario',
                'Por favor corrija los errores marcados en rojo'
            );
        } else {
            toastFormHelper.error(
                'Error al crear la venta',
                errorInfo.mensaje
            );
        }
    } finally {
        cargando.value = false;
    }
};

const getZonaNombre = (zonaId) => {
    const zona = zonas.value.find(z => z.id === parseInt(zonaId));
    return zona ? zona.nombre : '';
};

const getZonaPrecio = (zonaId) => {
    const zona = zonas.value.find(z => z.id === parseInt(zonaId));
    return zona ? parseFloat(zona.precio) : 0;
};
</script>

<template>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <ToastNotification ref="toastForm" />

        <form @submit.prevent="crearVenta" class="p-6 space-y-6">
            <!-- Selector de Evento -->
            <div class="mb-6">
                <InputLabel for="evento_id" required>Seleccione el Evento</InputLabel>
                <InputSelect 
                    v-model="form.evento_id" 
                    id="evento_id"
                    :error="errors.evento_id?.[0]"
                    :disabled="eventosActivos.length === 0">
                    <option value="">-- Seleccione un evento --</option>
                    <option 
                        v-for="evento in eventosActivos" 
                        :key="evento.id" 
                        :value="evento.id">
                        {{ evento.nombre }} - {{ new Date(evento.fecha).toLocaleDateString('es-PE') }} 
                        ({{ evento.lugar }})
                    </option>
                </InputSelect>
                <InputError :message="errors.evento_id?.[0]" />
            </div>

            <!-- Información del Evento Seleccionado -->
            <div v-if="eventoActivo"
                class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 border-l-4 border-primary-500 p-4 rounded-lg mb-6">
                <div class="flex items-start">
                    <svg class="w-6 h-6 text-primary-600 dark:text-primary-400 mt-0.5 mr-3 flex-shrink-0" fill="none"
                        stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <div class="flex-1">
                        <h4 class="font-semibold text-gray-900 dark:text-white mb-1">
                            {{ eventoActivo.nombre }}
                        </h4>
                        <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <p v-if="eventoActivo.fecha" class="flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                {{ new Date(eventoActivo.fecha).toLocaleDateString('es-PE', {
                                    year: 'numeric',
                                    month: 'long', day: 'numeric' }) }}
                            </p>
                            <p v-if="eventoActivo.hora" class="flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {{ eventoActivo.hora }}
                            </p>
                            <p v-if="eventoActivo.lugar" class="flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                {{ eventoActivo.lugar }}
                            </p>
                            <p class="flex items-center gap-2">
                                <span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                                    {{ eventoActivo.estado === '1' ? 'Próximo' : eventoActivo.estado === '2' ? 'Activo' : 'Finalizado' }}
                                </span>
                                <span class="text-xs">
                                    {{ zonas.length }} zona(s) disponible(s)
                                </span>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Alerta si no hay eventos activos -->
            <div v-else-if="eventosActivos.length === 0" class="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 p-4 rounded-lg mb-6">
                <div class="flex items-start">
                    <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" fill="none"
                        stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div>
                        <h4 class="font-semibold text-yellow-800 dark:text-yellow-300 mb-1">
                            No hay eventos activos
                        </h4>
                        <p class="text-sm text-yellow-700 dark:text-yellow-400">
                            Para vender entradas, primero debe activar un evento desde el módulo de Eventos.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Datos del Cliente -->
            <div class="border-b border-gray-200 dark:border-gray-700 pb-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                        <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        Datos del Cliente
                    </h3>
                    <span v-if="clienteEncontrado" 
                        class="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        Cliente Registrado
                    </span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <InputLabel for="cliente_dni" required>DNI del Cliente</InputLabel>
                        <div class="flex gap-2">
                            <InputText v-model="form.cliente_dni" id="cliente_dni" maxlength="8" placeholder="12345678"
                                :error="errors.cliente_dni?.[0]" :disabled="!eventoActivo" class="flex-1" />
                            <button type="button" @click="buscarCliente"
                                :disabled="buscandoCliente || form.cliente_dni.length !== 8 || !eventoActivo"
                                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
                                <Search class="w-4 h-4" />
                                {{ buscandoCliente ? "..." : "Buscar" }}
                            </button>
                        </div>
                        <InputError :message="errors.cliente_dni?.[0]" />
                    </div>

                    <div>
                        <InputLabel for="cliente_nombre" required>Nombre Completo</InputLabel>
                        <InputText v-model="form.cliente_nombre" id="cliente_nombre"
                            placeholder="Nombre completo del cliente" :error="errors.cliente_nombre?.[0]"
                            :disabled="!eventoActivo" />
                        <InputError :message="errors.cliente_nombre?.[0]" />
                    </div>

                    <div>
                        <InputLabel for="cliente_telefono">Teléfono</InputLabel>
                        <InputText v-model="form.cliente_telefono" id="cliente_telefono" placeholder="999999999"
                            maxlength="9" :disabled="!eventoActivo" />
                    </div>

                    <div>
                        <InputLabel for="cliente_email">Email</InputLabel>
                        <InputText v-model="form.cliente_email" id="cliente_email" type="email"
                            placeholder="cliente@ejemplo.com" :disabled="!eventoActivo" />
                    </div>
                </div>
            </div>

            <!-- Tickets -->
            <div class="border-b border-gray-200 dark:border-gray-700 pb-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                        <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
                        </svg>
                        Tickets ({{ form.tickets.length }}/3)
                    </h3>
                    <button type="button" @click="agregarTicket" :disabled="form.tickets.length >= 3 || !eventoActivo"
                        class="flex items-center gap-2 px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                        <Plus class="w-4 h-4" />
                        Agregar Ticket
                    </button>
                </div>

                <div class="space-y-4">
                    <div v-for="(ticket, index) in form.tickets" :key="index"
                        class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-sm font-semibold text-gray-900 dark:text-white">
                                Ticket #{{ index + 1 }}
                            </span>
                            <div class="flex gap-2">
                                <button type="button" @click="copiarDatosCliente(index)"
                                    :disabled="!form.cliente_dni || !form.cliente_nombre"
                                    class="text-xs text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50">
                                    Copiar datos del cliente
                                </button>
                                <button v-if="form.tickets.length > 1" type="button" @click="eliminarTicket(index)"
                                    class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300">
                                    <Trash2 class="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <div>
                                <InputLabel :for="'zona_' + index" required>Zona</InputLabel>
                                <InputSelect v-model="ticket.zona_id" :id="'zona_' + index" :disabled="!eventoActivo">
                                    <option value="">Seleccionar zona</option>
                                    <option v-for="zona in zonas" :key="zona.id" :value="zona.id"
                                        :disabled="zona.tickets_disponibles <= 0">
                                        {{ zona.nombre }} - S/ {{ zona.precio }}
                                        (Disp: {{ zona.tickets_disponibles }})
                                    </option>
                                </InputSelect>
                            </div>

                            <div>
                                <InputLabel :for="'dni_titular_' + index" required>DNI Titular</InputLabel>
                                <InputText v-model="ticket.dni_titular" :id="'dni_titular_' + index" maxlength="8"
                                    placeholder="87654321" :disabled="!eventoActivo" />
                            </div>

                            <div>
                                <InputLabel :for="'nombre_titular_' + index" required>Nombre Titular</InputLabel>
                                <InputText v-model="ticket.nombre_titular" :id="'nombre_titular_' + index"
                                    placeholder="Nombre del titular" :disabled="!eventoActivo" />
                            </div>
                        </div>

                        <!-- Mostrar precio del ticket seleccionado -->
                        <div v-if="ticket.zona_id" class="mt-3 text-sm text-gray-600 dark:text-gray-400">
                            <span class="font-medium">Precio:</span>
                            <span class="font-bold text-primary-600 dark:text-primary-400 ml-2">
                                S/ {{ getZonaPrecio(ticket.zona_id).toFixed(2) }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Datos de Pago -->
            <div class="pb-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    Datos de Pago
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <InputLabel for="metodo_pago" required>Método de Pago</InputLabel>
                        <InputSelect v-model="form.metodo_pago" id="metodo_pago" :disabled="!eventoActivo">
                            <option value="EFECTIVO">Efectivo</option>
                            <option value="TRANSFERENCIA">Transferencia</option>
                            <option value="YAPE">Yape</option>
                            <option value="PLIN">Plin</option>
                            <option value="TARJETA">Tarjeta</option>
                        </InputSelect>
                    </div>

                    <div>
                        <InputLabel for="nro_operacion">Nro. Operación</InputLabel>
                        <InputText v-model="form.nro_operacion" id="nro_operacion" placeholder="Ej: 123456789"
                            :disabled="!eventoActivo" />
                    </div>

                    <div class="md:col-span-2">
                        <InputLabel for="observaciones">Observaciones</InputLabel>
                        <InputTextarea v-model="form.observaciones" id="observaciones" rows="3"
                            placeholder="Notas adicionales sobre la venta..." :disabled="!eventoActivo" />
                    </div>
                </div>
            </div>

            <!-- Total y Botones -->
            <div class="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
                <div class="text-left">
                    <p class="text-sm text-gray-500 dark:text-gray-400">Total a pagar</p>
                    <p class="text-3xl font-bold text-gray-900 dark:text-white">
                        S/ {{ totalVenta.toFixed(2) }}
                    </p>
                </div>

                <div class="flex gap-3">
                    <ButtonCancel type="button" @click="$router.push('/admin/ventas')">
                        Cancelar
                    </ButtonCancel>
                    <ButtonSave type="submit" :disabled="cargando || !isFormValid || !eventoActivo"
                        :class="{ 'opacity-50 cursor-not-allowed': cargando || !isFormValid || !eventoActivo }">
                        <span v-if="cargando">Procesando...</span>
                        <span v-else>Confirmar Venta</span>
                    </ButtonSave>
                </div>
            </div>
        </form>
    </div>
</template>
