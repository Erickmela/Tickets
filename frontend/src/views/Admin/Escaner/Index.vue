<template>
    <div
        class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4 flex flex-col items-center justify-center">
        <!-- Header -->
        <div class="max-w-4xl w-full mb-6">
            <div
                class="bg-gradient-to-r from-white/15 to-white/5 backdrop-blur-xl rounded-3xl p-5 border border-white/20 shadow-2xl">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="relative">
                            <div class="absolute inset-0 bg-[#B3224D] rounded-2xl blur-lg opacity-50"></div>
                            <div
                                class="relative bg-gradient-to-br from-[#B3224D] to-[#8B1A3D] p-4 rounded-2xl shadow-lg">
                                <ScanLine class="w-7 h-7 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 class="text-2xl font-bold text-white">Escáner de Tickets</h1>
                            <p class="text-sm text-gray-300 flex items-center gap-2 mt-1">
                                <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                Validación en tiempo real
                            </p>
                        </div>
                    </div>
                    <button v-if="estadoEscaner === 'activo'" @click="detenerEscaner"
                        class="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 px-5 py-3 rounded-xl text-white font-semibold transition-all transform hover:scale-105 flex items-center gap-2 shadow-lg">
                        <X class="w-5 h-5" />
                        <span class="hidden sm:inline">Detener</span>
                    </button>
                </div>
            </div>
        </div>

        <div class="max-w-4xl w-full">
            <!-- Estado: Inactivo -->
            <div v-if="estadoEscaner === 'inactivo'" class="text-center">
                <div
                    class="bg-gradient-to-br from-white/15 to-white/5 backdrop-blur-md rounded-3xl p-12 border border-white/20 shadow-2xl">
                    <div class="relative inline-block mb-8">
                        <div class="absolute inset-0 bg-[#B3224D] rounded-full blur-2xl opacity-30 animate-pulse"></div>
                        <div
                            class="relative bg-gradient-to-br from-[#B3224D] to-[#8B1A3D] w-32 h-32 rounded-full mx-auto flex items-center justify-center shadow-2xl">
                            <Camera class="w-16 h-16 text-white" />
                        </div>
                    </div>

                    <h2 class="text-3xl font-bold text-white mb-4">Escáner de Tickets</h2>
                    <p class="text-gray-300 text-lg mb-8 max-w-md mx-auto">
                        Activa tu cámara para comenzar a validar los códigos QR de los tickets en tiempo real
                    </p>

                    <button @click="iniciarEscaner" :disabled="cargando"
                        class="bg-gradient-to-r from-[#B3224D] to-[#8B1A3D] hover:from-[#8B1A3D] hover:to-[#6B1030] disabled:from-gray-500 disabled:to-gray-600 px-10 py-5 rounded-2xl text-white font-bold text-xl transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed inline-flex items-center gap-4 shadow-2xl shadow-[#B3224D]/30">
                        <Camera v-if="!cargando" class="w-7 h-7" />
                        <Loader2 v-else class="w-7 h-7 animate-spin" />
                        <span>{{ cargando ? 'Iniciando cámara...' : 'Activar Cámara' }}</span>
                    </button>
                </div>
            </div>

            <!-- Estado: Activo (Escaneando) -->
            <div v-else-if="estadoEscaner === 'activo'" class="space-y-4">
                <!-- Video Stream con diseño mejorado -->
                <div class="relative rounded-3xl overflow-hidden shadow-[0_20px_60px_-15px_rgba(179,34,77,0.5)]">
                    <video ref="videoRef" autoplay playsinline muted webkit-playsinline class="w-full"
                        style="height: 70vh; object-fit: cover; display: block !important; background: #000;">
                        Tu navegador no soporta video
                    </video>

                    <!-- Overlay con gradiente sutil -->
                    <div
                        class="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/30 pointer-events-none">
                    </div>

                    <!-- Marco de escaneo mejorado -->
                    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div class="relative animate-pulse-slow" style="width: 300px; height: 300px;">
                            <!-- Esquinas con sombra y glow -->
                            <div
                                class="absolute -top-2 -left-2 w-20 h-20 border-t-[5px] border-l-[5px] border-[#B3224D] rounded-tl-2xl shadow-lg shadow-[#B3224D]/50 animate-corner">
                            </div>
                            <div class="absolute -top-2 -right-2 w-20 h-20 border-t-[5px] border-r-[5px] border-[#B3224D] rounded-tr-2xl shadow-lg shadow-[#B3224D]/50 animate-corner"
                                style="animation-delay: 0.1s"></div>
                            <div class="absolute -bottom-2 -left-2 w-20 h-20 border-b-[5px] border-l-[5px] border-[#B3224D] rounded-bl-2xl shadow-lg shadow-[#B3224D]/50 animate-corner"
                                style="animation-delay: 0.2s"></div>
                            <div class="absolute -bottom-2 -right-2 w-20 h-20 border-b-[5px] border-r-[5px] border-[#B3224D] rounded-br-2xl shadow-lg shadow-[#B3224D]/50 animate-corner"
                                style="animation-delay: 0.3s"></div>

                            <!-- Línea de escaneo más visible -->
                            <div
                                class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#B3224D] to-transparent shadow-[0_0_20px_rgba(179,34,77,0.8)] animate-scan">
                            </div>

                            <!-- Área de enfoque con puntos de esquina animados -->
                            <div class="absolute inset-4 border-2 border-dashed border-[#B3224D]/30 rounded-2xl"></div>
                        </div>
                    </div>

                    <!-- Mensaje flotante central -->
                    <div class="absolute inset-0 flex items-end justify-center pb-24 pointer-events-none">
                        <div
                            class="bg-gradient-to-r from-[#B3224D] to-[#8B1A3D] backdrop-blur-md px-8 py-4 rounded-2xl border-2 border-white/20 shadow-2xl transform animate-float">
                            <div class="flex items-center gap-3">
                                <div v-if="procesando" class="flex gap-1">
                                    <div class="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                                    <div class="w-2 h-2 bg-white rounded-full animate-bounce"
                                        style="animation-delay: 0.1s"></div>
                                    <div class="w-2 h-2 bg-white rounded-full animate-bounce"
                                        style="animation-delay: 0.2s"></div>
                                </div>
                                <ScanLine v-else class="w-6 h-6 text-white animate-pulse" />
                                <p class="text-white font-bold text-lg">
                                    {{ procesando ? 'Validando ticket...' : 'Apunta al código QR' }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <canvas ref="canvasRef" class="hidden"></canvas>
                </div>
            </div>
        </div>

        <!-- Modal de resultado -->
        <DialogModal :show="mostrarResultado" @close="cerrarResultado" max-width="2xl">
            <template #content>
                <div class="p-6">
                    <!-- Resultado Exitoso -->
                    <div v-if="resultado?.success" class="text-center">
                        <div class="bg-green-100 w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center">
                            <CheckCircle class="w-16 h-16 text-green-600" />
                        </div>
                        <h2 class="text-3xl font-bold text-green-600 mb-2">{{ resultado.message }}</h2>
                        <p class="text-gray-600 mb-6">Ticket validado correctamente</p>

                        <!-- Método de seguridad -->
                        <div v-if="resultado.metodo_seguridad"
                            class="mb-6 inline-flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-lg">
                            <Shield class="w-5 h-5 text-blue-600" />
                            <span class="text-sm font-medium text-blue-900">
                                {{ resultado.metodo_seguridad === 'ENCRIPTADO_AES256' ? 'Encriptación AES-256' : 'UUIDDirecto' }}
                            </span>
                        </div>

                        <!-- Datos del ticket para verificación -->
                        <div class="bg-gray-50 rounded-xl p-6 mb-6 text-left">
                            <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                <User class="w-5 h-5 text-[#B3224D]" />
                                Datos del Titular
                            </h3>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <p class="text-sm text-gray-500 mb-1">DNI</p>
                                    <p class="text-2xl font-bold text-gray-900">{{ resultado.ticket.dni_titular }}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500 mb-1">Nombre</p>
                                    <p class="text-lg font-bold text-gray-900">{{ resultado.ticket.nombre_titular }}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500 mb-1">Zona</p>
                                    <p class="text-lg font-semibold text-[#B3224D]">{{ resultado.ticket.zona }}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500 mb-1">Precio</p>
                                    <p class="text-lg font-semibold text-gray-900">S/ {{ resultado.ticket.precio }}</p>
                                </div>
                            </div>
                        </div>

                        <!-- Instrucciones de verificación -->
                        <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6 text-left">
                            <h4 class="font-bold text-yellow-900 mb-3 flex items-center gap-2">
                                <AlertCircle class="w-5 h-5" />
                                Verificación Obligatoria
                            </h4>
                            <ol class="list-decimal list-inside space-y-2 text-sm text-yellow-900">
                                <li v-for="(instruccion, index) in resultado.instrucciones" :key="index">
                                    {{ instruccion }}
                                </li>
                            </ol>
                        </div>

                        <button @click="continuarEscaneando"
                            class="w-full bg-[#B3224D] hover:bg-[#8B1A3D] px-6 py-4 rounded-xl text-white font-bold transition-colors">
                            Continuar Escaneando
                        </button>
                    </div>

                    <!-- Resultado Error -->
                    <div v-else class="text-center">
                        <div class="bg-red-100 w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center">
                            <XCircle class="w-16 h-16 text-red-600" />
                        </div>
                        <h2 class="text-3xl font-bold text-red-600 mb-2">{{ resultado?.error || 'ERROR' }}</h2>
                        <p class="text-gray-700 text-lg mb-6">{{ resultado?.message }}</p>

                        <!-- Alerta de seguridad -->
                        <div v-if="resultado?.alerta" class="bg-red-50 border-2 border-red-500 rounded-xl p-6 mb-6">
                            <div class="flex items-center gap-3 mb-2">
                                <AlertTriangle class="w-8 h-8 text-red-600" />
                                <h3 class="text-xl font-bold text-red-900">ALERTA DE SEGURIDAD</h3>
                            </div>
                            <p class="text-red-900 font-semibold text-lg">{{ resultado.alerta }}</p>
                        </div>

                        <!-- Información adicional para tickets ya usados -->
                        <div v-if="resultado?.fecha_uso" class="bg-gray-50 rounded-xl p-4 mb-6 text-left">
                            <p class="text-sm text-gray-600 mb-2">Fecha de uso anterior:</p>
                            <p class="text-lg font-bold text-gray-900">{{ formatearFecha(resultado.fecha_uso) }}</p>
                            <p v-if="resultado.validador" class="text-sm text-gray-600 mt-2">
                                Validado por: <span class="font-semibold">{{ resultado.validador }}</span>
                            </p>
                            <div v-if="resultado.ticket" class="mt-4 pt-4 border-t border-gray-200">
                                <p class="text-sm text-gray-500">Titular:</p>
                                <p class="font-bold text-gray-900">{{ resultado.ticket.nombre_titular }}</p>
                                <p class="text-sm text-gray-500 mt-1">DNI: {{ resultado.ticket.dni_titular }}</p>
                            </div>
                        </div>

                        <div class="flex gap-3">
                            <button @click="continuarEscaneando"
                                class="flex-1 bg-gray-200 hover:bg-gray-300 px-6 py-4 rounded-xl text-gray-900 font-bold transition-colors">
                                Continuar Escaneando
                            </button>
                            <button @click="cerrarResultado"
                                class="flex-1 bg-[#B3224D] hover:bg-[#8B1A3D] px-6 py-4 rounded-xl text-white font-bold transition-colors">
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            </template>
        </DialogModal>
    </div>
</template>

<script setup>
import { ref, onUnmounted, onMounted } from 'vue';
import { Camera, ScanLine, X, CheckCircle, XCircle, User, AlertCircle, AlertTriangle, Info, Shield, Loader2, QrCode, Sun } from 'lucide-vue-next';
import DialogModal from '@/components/DialogModal.vue';
import { validacionesService } from '@/services/validacionesService';
import jsQR from 'jsqr';

// Referencias
const videoRef = ref(null);
const canvasRef = ref(null);
const stream = ref(null);
const animationFrameId = ref(null);

// Estados
const estadoEscaner = ref('inactivo'); // 'inactivo', 'activo'
const cargando = ref(false);
const procesando = ref(false);
const mostrarResultado = ref(false);
const resultado = ref(null);

// Iniciar escáner
const iniciarEscaner = async () => {
    try {
        cargando.value = true;

        // ULTRA SIMPLE: Solo solicitar video sin restricciones
        const constraints = { video: true };

        stream.value = await navigator.mediaDevices.getUserMedia(constraints);

        estadoEscaner.value = 'activo';

        // Esperar a que el DOM se actualice
        await new Promise(resolve => setTimeout(resolve, 100));

        if (videoRef.value) {
            // Método 1: srcObject directo
            videoRef.value.srcObject = stream.value;

            // Método 2: Forzar atributos
            videoRef.value.setAttribute('autoplay', '');
            videoRef.value.setAttribute('playsinline', '');
            videoRef.value.setAttribute('muted', '');

            // Método 3: Reproducir manualmente después de un delay
            setTimeout(async () => {
                try {
                    videoRef.value.muted = true; // Importante para autoplay
                    await videoRef.value.play();

                    // Iniciar detección después de que el video esté visible
                    setTimeout(() => {
                        comenzarDeteccion();
                    }, 1000);
                } catch (playErr) {
                    // Intentar una vez más
                    setTimeout(() => {
                        videoRef.value.play().catch(() => { });
                    }, 500);
                }
            }, 300);
        }
    } catch (error) {
        alert('No se pudo acceder a la cámara. Verifica los permisos en tu navegador.');
        estadoEscaner.value = 'inactivo';
    } finally {
        cargando.value = false;
    }
};

// Detener escáner
const detenerEscaner = () => {
    if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop());
        stream.value = null;
    }
    if (animationFrameId.value) {
        cancelAnimationFrame(animationFrameId.value);
        animationFrameId.value = null;
    }
    estadoEscaner.value = 'inactivo';
};

// Comenzar detección de QR
const comenzarDeteccion = () => {
    const detectar = () => {
        if (estadoEscaner.value !== 'activo') {
            return;
        }

        if (procesando.value) {
            animationFrameId.value = requestAnimationFrame(detectar);
            return;
        }

        const video = videoRef.value;
        const canvas = canvasRef.value;

        if (video && canvas && video.readyState === video.HAVE_ENOUGH_DATA) {
            // Actualizar tamaño del canvas
            if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }

            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height, {
                inversionAttempts: 'dontInvert',
            });

            if (code) {
                procesarQR(code.data);
                return; // Detener detección mientras procesa
            }
        }

        animationFrameId.value = requestAnimationFrame(detectar);
    };

    detectar();
};

// Procesar código QR detectado
const procesarQR = async (codigoQR) => {
    if (procesando.value) return;

    procesando.value = true;

    try {
        // Llamar al API de validación
        const response = await validacionesService.validarTicket(codigoQR);
        resultado.value = response;
        mostrarResultado.value = true;
        detenerEscaner();
    } catch (error) {
        // Manejar diferentes tipos de errores
        if (error.response?.data) {
            const errorData = error.response.data;

            // Error de validación de UUID
            if (errorData.codigo_uuid) {
                resultado.value = {
                    success: false,
                    error: 'CÓDIGO QR INVÁLIDO',
                    message: 'El código escaneado no es un ticket válido. Asegúrate de escanear un ticket de este sistema.',
                    alerta: 'Este no es un ticket válido - Usa solo tickets generados por el sistema'
                };
            } else {
                resultado.value = errorData;
            }
        } else {
            resultado.value = {
                success: false,
                error: 'Error del sistema',
                message: 'No se pudo validar el ticket. Intenta nuevamente.'
            };
        }

        mostrarResultado.value = true;
        detenerEscaner();
    } finally {
        procesando.value = false;
    }
};

// Continuar escaneando
const continuarEscaneando = () => {
    resultado.value = null;
    mostrarResultado.value = false;
    iniciarEscaner();
};

// Cerrar resultado
const cerrarResultado = () => {
    resultado.value = null;
    mostrarResultado.value = false;
};

// Formatear fecha
const formatearFecha = (fecha) => {
    if (!fecha) return '';
    const date = new Date(fecha);
    return date.toLocaleString('es-PE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Limpiar al desmontar
onUnmounted(() => {
    detenerEscaner();
});
</script>

<style scoped>
/* Animación de escaneo mejorada */
@keyframes scan {

    0%,
    100% {
        top: 0;
        opacity: 1;
        transform: scaleX(1);
    }

    50% {
        top: 100%;
        opacity: 0.8;
        transform: scaleX(0.95);
    }
}

.animate-scan {
    animation: scan 2.5s ease-in-out infinite;
    box-shadow: 0 0 30px 4px rgba(179, 34, 77, 0.9),
        0 0 60px 8px rgba(179, 34, 77, 0.5);
}

/* Animación de esquinas */
@keyframes corner {

    0%,
    100% {
        opacity: 1;
        transform: scale(1);
    }

    50% {
        opacity: 0.6;
        transform: scale(0.95);
    }
}

.animate-corner {
    animation: corner 1.5s ease-in-out infinite;
}

/* Animación flotante */
@keyframes float {

    0%,
    100% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-10px);
    }
}

.animate-float {
    animation: float 3s ease-in-out infinite;
}

/* Pulse lento */
@keyframes pulse-slow {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.8;
    }
}

.animate-pulse-slow {
    animation: pulse-slow 3s ease-in-out infinite;
}

/* Asegurar que el video se muestre correctamente */
video {
    background-color: #000;
}

video::-webkit-media-controls {
    display: none !important;
}

video::-webkit-media-controls-enclosure {
    display: none !important;
}

/* Efecto de brillo en hover para las tarjetas */
.hover\:scale-105:hover {
    transform: scale(1.05);
    filter: brightness(1.1);
}
</style>
