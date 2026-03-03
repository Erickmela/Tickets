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
                presentacion_id: "",
                dni_titular: "",
                nombre_titular: "",
            },
        ],
    };
}

const form = ref(getFormData());
const eventosActivos = ref([]);
const evento_seleccionado = ref(null);
const presentaciones = ref([]);
const zonas = ref([]);
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
        form.value.cliente_dni.length === 8 &&
        form.value.cliente_nombre.trim() !== "" &&
        form.value.tickets.length > 0 &&
        form.value.tickets.every(t =>
            t.presentacion_id &&
            t.zona_id &&
            t.dni_titular.length === 8 &&
            t.nombre_titular.trim() !== ""
        )
    );
});

// Computed: Total de la venta
const totalVenta = computed(() => {
    return form.value.tickets.reduce((total, ticket) => {
        const zona = zonas.value.find(z => z.id === parseInt(ticket.zona_id));
        return total + (zona ? parseFloat(zona.precio) : 0);
    }, 0);
});

// Watch: Emitir cambios
watch([form, totalVenta, evento_seleccionado], () => {
    emit("update:formData", {
        ...form.value,
        total: totalVenta.value,
        evento: evento_seleccionado.value
    });
}, { deep: true });

// Watch: Emitir validación
watch(isFormValid, (valid) => {
    emit("update:validation", valid);
});

// Watch: Limpiar cliente si DNI cambia
watch(() => form.value.cliente_dni, (newDni) => {
    if (newDni.length !== 8) {
        clienteEncontrado.value = false;
    }
});

// Watch: Cargar presentaciones cuando se selecciona evento
watch(() => form.value.evento_id, async (newEventoId, oldEventoId) => {
    if (newEventoId) {
        await cargarPresentacionesEvento(newEventoId);

        // Limpiar tickets si cambió el evento
        if (oldEventoId && oldEventoId !== newEventoId) {
            form.value.tickets = [{
                presentacion_id: "",
                zona_id: "",
                dni_titular: "",
                nombre_titular: ""
            }];
        }
    } else {
        presentaciones.value = [];
        zonas.value = [];
        evento_seleccionado.value = null;
    }
});

// Función para cargar presentaciones del evento
const cargarPresentacionesEvento = async (eventoId) => {
    try {
        // Cargar evento completo
        await eventosStore.fetchEvento(eventoId);
        evento_seleccionado.value = eventosStore.evento;

        // Cargar presentaciones del evento
        const response = await eventosStore.fetchPresentacionesByEvento(eventoId);
        presentaciones.value = response;

        if (presentaciones.value.length === 0) {
            toastFormHelper.warning('Este evento no tiene presentaciones configuradas');
        }
    } catch (error) {
        console.error('Error al cargar presentaciones:', error);
        toastFormHelper.error('Error al cargar las presentaciones del evento');
        presentaciones.value = [];
    }
};

// Función para cargar zonas cuando se selecciona una presentación en un ticket
const cargarZonasPresentacion = async (presentacionId, ticketIndex) => {
    try {
        const zonasData = await eventosStore.fetchZonasByPresentacion(presentacionId);
        zonas.value = zonasData;

        if (zonasData.length === 0) {
            toastFormHelper.warning('Esta presentación no tiene zonas disponibles');
        }
    } catch (error) {
        console.error('Error al cargar zonas:', error);
        toastFormHelper.error('Error al cargar las zonas de la presentación');
        zonas.value = [];
    }
};

// Watch: Cargar zonas cuando cambia la presentación en el primer ticket
watch(() => form.value.tickets[0]?.presentacion_id, async (newPresentacionId) => {
    if (newPresentacionId) {
        await cargarZonasPresentacion(newPresentacionId, 0);
    } else {
        zonas.value = [];
    }
});

onMounted(async () => {
    try {
        // Cargar eventos para select (solo id, encoded_id, nombre)
        eventosActivos.value = await eventosStore.fetchEventosSelect();

        // Si solo hay un evento activo, seleccionarlo automáticamente
        if (eventosActivos.value.length === 1) {
            form.value.evento_id = eventosActivos.value[0].id;
        }

        // Emitir datos iniciales
        emit("update:formData", {
            ...form.value,
            total: totalVenta.value,
            evento: evento_seleccionado.value
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
            presentacion_id: "",
            zona_id: "",
            dni_titular: "",
            nombre_titular: ""
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
        // Preparar datos: convertir IDs de string a número
        const ventaData = {
            ...form.value,
            evento_id: parseInt(form.value.evento_id),
            tickets: form.value.tickets.map(ticket => ({
                zona_id: parseInt(ticket.zona_id),
                presentacion_id: parseInt(ticket.presentacion_id),
                dni_titular: ticket.dni_titular,
                nombre_titular: ticket.nombre_titular
            }))
        };

        const data = await ventasStore.crearVenta(ventaData);
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

        <form @submit.prevent="crearVenta" class="p-6 space-y-5">
            <!-- Selector de Evento -->
            <div>
                <InputLabel for="evento_id" required>Evento</InputLabel>
                <InputSelect v-model="form.evento_id" id="evento_id" :error="errors.evento_id?.[0]"
                    :disabled="eventosActivos.length === 0">
                    <option value="">-- Seleccione un evento --</option>
                    <option v-for="evento in eventosActivos" :key="evento.id" :value="evento.id">
                        {{ evento.nombre }}
                    </option>
                </InputSelect>
                <InputError :message="errors.evento_id?.[0]" />
            </div>

            <!-- Alerta si no hay eventos activos -->
            <div v-if="eventosActivos.length === 0"
                class="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 p-3 rounded">
                <p class="text-sm text-yellow-800 dark:text-yellow-300">
                    <strong>No hay eventos activos.</strong> Active un evento desde el módulo de Eventos para vender
                    entradas.
                </p>
            </div>

            <!-- Alerta si no hay presentaciones -->
            <div v-if="evento_seleccionado && presentaciones.length === 0"
                class="bg-orange-50 dark:bg-orange-900/20 border-l-4 border-orange-500 p-3 rounded">
                <p class="text-sm text-orange-800 dark:text-orange-300">
                    <strong>Sin presentaciones.</strong> Configure al menos una presentación para este evento.
                </p>
            </div>

            <!-- Datos del Cliente -->
            <div class="border-t pt-5">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="text-base font-semibold text-gray-900 dark:text-white">Datos del Cliente</h3>
                    <span v-if="clienteEncontrado"
                        class="text-xs px-2 py-1 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded">
                        ✓ Registrado
                    </span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <InputLabel for="cliente_dni" required>DNI</InputLabel>
                        <div class="flex gap-2">
                            <InputText v-model="form.cliente_dni" id="cliente_dni" maxlength="8" placeholder="12345678"
                                :error="errors.cliente_dni?.[0]" :disabled="!form.evento_id" class="flex-1" />
                            <button type="button" @click="buscarCliente"
                                :disabled="buscandoCliente || form.cliente_dni.length !== 8 || !form.evento_id"
                                class="px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed">
                                <Search class="w-4 h-4" />
                            </button>
                        </div>
                        <InputError :message="errors.cliente_dni?.[0]" />
                    </div>

                    <div>
                        <InputLabel for="cliente_nombre" required>Nombre Completo</InputLabel>
                        <InputText v-model="form.cliente_nombre" id="cliente_nombre" placeholder="Nombre completo"
                            :error="errors.cliente_nombre?.[0]" :disabled="!form.evento_id" />
                        <InputError :message="errors.cliente_nombre?.[0]" />
                    </div>

                    <div>
                        <InputLabel for="cliente_telefono">Teléfono</InputLabel>
                        <InputText v-model="form.cliente_telefono" id="cliente_telefono" placeholder="999999999"
                            maxlength="9" :disabled="!form.evento_id" />
                    </div>

                    <div>
                        <InputLabel for="cliente_email">Email</InputLabel>
                        <InputText v-model="form.cliente_email" id="cliente_email" type="email"
                            placeholder="cliente@ejemplo.com" :disabled="!form.evento_id" />
                    </div>
                </div>
            </div>

            <!-- Tickets -->
            <div class="border-t pt-5">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="text-base font-semibold text-gray-900 dark:text-white">
                        Tickets ({{ form.tickets.length }}/3)
                    </h3>
                    <button type="button" @click="agregarTicket"
                        :disabled="form.tickets.length >= 3 || !form.evento_id"
                        class="flex items-center gap-1 px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed">
                        <Plus class="w-4 h-4" />
                        Agregar
                    </button>
                </div>

                <div class="space-y-3">
                    <div v-for="(ticket, index) in form.tickets" :key="index"
                        class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                                #{{ index + 1 }}
                            </span>
                            <div class="flex gap-2 items-center">
                                <button type="button" @click="copiarDatosCliente(index)"
                                    :disabled="!form.cliente_dni || !form.cliente_nombre"
                                    class="text-xs text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50">
                                    Copiar cliente
                                </button>
                                <button v-if="form.tickets.length > 1" type="button" @click="eliminarTicket(index)"
                                    class="text-red-600 hover:text-red-700 dark:text-red-400">
                                    <Trash2 class="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                                <InputLabel :for="'presentacion_' + index" required>Presentación</InputLabel>
                                <InputSelect v-model="ticket.presentacion_id" :id="'presentacion_' + index"
                                    @change=" cargarZonasPresentacion(ticket.presentacion_id, index)"
                                    :disabled="!form.evento_id || presentaciones.length === 0">
                                    <option value="">Seleccionar</option>
                                    <option v-for="presentacion in presentaciones" :key="presentacion.id"
                                        :value="presentacion.id">
                                        {{ presentacion.nombre_display }}
                                    </option>
                                </InputSelect>
                            </div>

                            <div>
                                <InputLabel :for="'zona_' + index" required>Zona</InputLabel>
                                <InputSelect v-model="ticket.zona_id" :id="'zona_' + index"
                                    :disabled="!ticket.presentacion_id || zonas.length === 0">
                                    <option value="">Seleccionar</option>
                                    <option v-for="zona in zonas" :key="zona.id" :value="zona.id"
                                        :disabled="!zona.tiene_disponibilidad">
                                        {{ zona.nombre }} - S/ {{ zona.precio }}
                                        ({{ zona.tickets_disponibles }} disp.)
                                    </option>
                                </InputSelect>
                            </div>

                            <div>
                                <InputLabel :for="'dni_titular_' + index" required>DNI Titular</InputLabel>
                                <InputText v-model="ticket.dni_titular" :id="'dni_titular_' + index" maxlength="8"
                                    placeholder="12345678" :disabled="!form.evento_id" />
                            </div>

                            <div>
                                <InputLabel :for="'nombre_titular_' + index" required>Nombre Titular</InputLabel>
                                <InputText v-model="ticket.nombre_titular" :id="'nombre_titular_' + index"
                                    placeholder="Nombre completo" :disabled="!form.evento_id" />
                            </div>
                        </div>

                        <div v-if="ticket.zona_id" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                            Precio: <span class="font-semibold text-primary-600 dark:text-primary-400">S/ {{
                                getZonaPrecio(ticket.zona_id).toFixed(2) }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Datos de Pago -->
            <div class="border-t pt-5">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3">Datos de Pago</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <InputLabel for="metodo_pago" required>Método de Pago</InputLabel>
                        <InputSelect v-model="form.metodo_pago" id="metodo_pago" :disabled="!form.evento_id">
                            <option value="EFECTIVO">Efectivo</option>
                            <option value="TRANSFERENCIA">Transferencia</option>
                            <option value="YAPE">Yape</option>
                            <option value="PLIN">Plin</option>
                            <option value="TARJETA">Tarjeta</option>
                        </InputSelect>
                    </div>

                    <div>
                        <InputLabel for="nro_operacion">Nro. Operación</InputLabel>
                        <InputText v-model="form.nro_operacion" id="nro_operacion" placeholder="123456789"
                            :disabled="!form.evento_id" />
                    </div>

                    <div class="md:col-span-2">
                        <InputLabel for="observaciones">Observaciones</InputLabel>
                        <InputTextarea v-model="form.observaciones" id="observaciones" rows="2"
                            placeholder="Notas adicionales..." :disabled="!form.evento_id" />
                    </div>
                </div>
            </div>

            <!-- Total y Botones -->
            <div class="flex items-center justify-between pt-5 border-t border-gray-200 dark:border-gray-700">
                <div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Total</p>
                    <p class="text-2xl font-bold text-gray-900 dark:text-white">
                        S/ {{ totalVenta.toFixed(2) }}
                    </p>
                </div>

                <div class="flex gap-3">
                    <ButtonCancel type="button" @click="$router.push('/admin/ventas')">
                        Cancelar
                    </ButtonCancel>
                    <ButtonSave type="submit" :disabled="cargando || !isFormValid || !form.evento_id"
                        :class="{ 'opacity-50 cursor-not-allowed': cargando || !isFormValid || !form.evento_id }">
                        {{ cargando ? 'Procesando...' : 'Confirmar Venta' }}
                    </ButtonSave>
                </div>
            </div>
        </form>
    </div>
</template>
