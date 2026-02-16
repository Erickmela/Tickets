<template>
  <AdmLayout>
    <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div class="max-w-7xl mx-auto">
        
        <!-- Header con Selector de Evento -->
        <div class="mb-8">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 class="text-3xl font-bold text-white mb-2">Dashboard de Eventos</h1>
              <p class="text-gray-400">Estadísticas y métricas en tiempo real</p>
            </div>
            
            <!-- Selector de Evento -->
            <div class="w-full md:w-80">
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Seleccionar Evento
              </label>
              <select
                v-model="eventoSeleccionado"
                @change="cargarEstadisticas"
                class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white 
                       focus:ring-2 focus:ring-[#B3224D] focus:border-transparent transition-all
                       backdrop-blur-sm"
              >
                <option value="">-- Seleccione un evento --</option>
                <option v-for="evento in eventos" :key="evento.id" :value="evento.id">
                  {{ evento.nombre }} - {{ formatDate(evento.fecha) }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="cargando" class="flex items-center justify-center py-20">
          <div class="flex flex-col items-center gap-4">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-[#B3224D] border-t-transparent"></div>
            <p class="text-gray-400">Cargando estadísticas...</p>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="!eventoSeleccionado" class="text-center py-20">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-800 mb-4">
            <BarChart3 class="w-8 h-8 text-gray-600" />
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">Seleccione un Evento</h3>
          <p class="text-gray-400">Elija un evento para ver sus estadísticas y métricas</p>
        </div>

        <!-- Dashboard Content -->
        <div v-else-if="estadisticas">
          
          <!-- Tarjetas de Resumen -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            
            <!-- Total de Ventas -->
            <div class="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-blue-500/20 rounded-lg">
                  <ShoppingCart class="w-6 h-6 text-blue-400" />
                </div>
                <span class="text-xs font-medium text-blue-300 bg-blue-500/20 px-2 py-1 rounded-full">
                  Ventas
                </span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-1">{{ estadisticas.ventas.total_ventas }}</h3>
              <p class="text-sm text-blue-200">Total de Ventas</p>
            </div>

            <!-- Ingresos Totales -->
            <div class="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-sm border border-green-500/30 rounded-xl p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-green-500/20 rounded-lg">
                  <DollarSign class="w-6 h-6 text-green-400" />
                </div>
                <span class="text-xs font-medium text-green-300 bg-green-500/20 px-2 py-1 rounded-full">
                  Ingresos
                </span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-1">S/ {{ formatNumber(estadisticas.ventas.ingresos_totales) }}</h3>
              <p class="text-sm text-green-200">Ganancia Total</p>
            </div>

            <!-- Tickets Vendidos -->
            <div class="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-purple-500/20 rounded-lg">
                  <Ticket class="w-6 h-6 text-purple-400" />
                </div>
                <span class="text-xs font-medium text-purple-300 bg-purple-500/20 px-2 py-1 rounded-full">
                  Tickets
                </span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-1">{{ estadisticas.tickets.total_vendidos }}</h3>
              <p class="text-sm text-purple-200">de {{ estadisticas.capacidad.total }} disponibles</p>
            </div>

            <!-- Ocupación -->
            <div class="bg-gradient-to-br from-[#B3224D]/20 to-[#8B1A3D]/20 backdrop-blur-sm border border-[#B3224D]/30 rounded-xl p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-[#B3224D]/20 rounded-lg">
                  <TrendingUp class="w-6 h-6 text-[#B3224D]" />
                </div>
                <span class="text-xs font-medium text-pink-300 bg-[#B3224D]/20 px-2 py-1 rounded-full">
                  Ocupación
                </span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-1">{{ estadisticas.capacidad.porcentaje_ocupacion }}%</h3>
              <p class="text-sm text-pink-200">Capacidad Ocupada</p>
            </div>

          </div>

          <!-- Fila 2: Estadísticas por Zona y Métodos de Pago -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            
            <!-- Ventas por Zona -->
            <div class="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
              <div class="flex items-center gap-3 mb-6">
                <MapPin class="w-5 h-5 text-[#B3224D]" />
                <h2 class="text-xl font-bold text-white">Ventas por Zona</h2>
              </div>
              
              <div class="space-y-4">
                <div v-for="zona in estadisticas.zonas" :key="zona.id" class="space-y-2">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-300">{{ zona.nombre }}</span>
                    <span class="text-sm font-bold text-white">S/ {{ formatNumber(zona.ingresos) }}</span>
                  </div>
                  
                  <div class="flex items-center gap-3">
                    <!-- Barra de progreso -->
                    <div class="flex-1 bg-gray-700 rounded-full h-2 overflow-hidden">
                      <div 
                        class="h-full bg-gradient-to-r from-[#B3224D] to-[#E63E6D] rounded-full transition-all duration-500"
                        :style="{ width: `${zona.porcentaje_ocupacion}%` }"
                      ></div>
                    </div>
                    <span class="text-xs text-gray-400 w-12 text-right">{{ zona.porcentaje_ocupacion }}%</span>
                  </div>
                  
                  <div class="flex items-center justify-between text-xs text-gray-500">
                    <span>{{ zona.tickets_vendidos }} / {{ zona.capacidad_maxima }} tickets</span>
                    <span>S/ {{ formatNumber(zona.precio) }} c/u</span>
                  </div>
                </div>

                <div v-if="estadisticas.zonas.length === 0" class="text-center py-8 text-gray-500">
                  No hay zonas configuradas
                </div>
              </div>
            </div>

            <!-- Métodos de Pago -->
            <div class="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
              <div class="flex items-center gap-3 mb-6">
                <CreditCard class="w-5 h-5 text-[#B3224D]" />
                <h2 class="text-xl font-bold text-white">Métodos de Pago</h2>
              </div>
              
              <div class="space-y-4">
                <div v-for="metodo in estadisticas.ventas.por_metodo_pago" :key="metodo.metodo" 
                     class="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <div class="w-2 h-2 rounded-full bg-[#B3224D]"></div>
                      <span class="font-medium text-white">{{ metodo.metodo }}</span>
                    </div>
                    <p class="text-sm text-gray-400">{{ metodo.cantidad_ventas }} ventas</p>
                  </div>
                  <div class="text-right">
                    <p class="text-lg font-bold text-white">S/ {{ formatNumber(metodo.monto_total) }}</p>
                    <p class="text-xs text-gray-400">
                      {{ calcularPorcentaje(metodo.monto_total, estadisticas.ventas.ingresos_totales) }}%
                    </p>
                  </div>
                </div>

                <div v-if="estadisticas.ventas.por_metodo_pago.length === 0" class="text-center py-8 text-gray-500">
                  No hay ventas registradas
                </div>
              </div>
            </div>

          </div>

          <!-- Fila 3: Estado de Tickets y Info del Evento -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <!-- Estado de Tickets -->
            <div class="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
              <div class="flex items-center gap-3 mb-6">
                <BarChart3 class="w-5 h-5 text-[#B3224D]" />
                <h2 class="text-xl font-bold text-white">Estado de Tickets</h2>
              </div>
              
              <div class="space-y-4">
                <!-- Activos -->
                <div class="flex items-center justify-between p-4 bg-green-500/10 rounded-lg border border-green-500/30">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-green-500/20 rounded-lg">
                      <CheckCircle class="w-5 h-5 text-green-400" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-green-200">Activos</p>
                      <p class="text-xs text-green-300/70">Tickets válidos</p>
                    </div>
                  </div>
                  <span class="text-2xl font-bold text-green-400">{{ estadisticas.tickets.activos }}</span>
                </div>

                <!-- Usados -->
                <div class="flex items-center justify-between p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-blue-500/20 rounded-lg">
                      <CheckCircle class="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-blue-200">Usados</p>
                      <p class="text-xs text-blue-300/70">Ya validados</p>
                    </div>
                  </div>
                  <span class="text-2xl font-bold text-blue-400">{{ estadisticas.tickets.usados }}</span>
                </div>

                <!-- Anulados -->
                <div class="flex items-center justify-between p-4 bg-red-500/10 rounded-lg border border-red-500/30">
                  <div class="flex items-center gap-3">
                    <div class="p-2 bg-red-500/20 rounded-lg">
                      <XCircle class="w-5 h-5 text-red-400" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-red-200">Anulados</p>
                      <p class="text-xs text-red-300/70">Cancelados</p>
                    </div>
                  </div>
                  <span class="text-2xl font-bold text-red-400">{{ estadisticas.tickets.anulados }}</span>
                </div>
              </div>
            </div>

            <!-- Info del Evento -->
            <div class="bg-gradient-to-br from-[#B3224D]/20 to-[#8B1A3D]/20 backdrop-blur-sm border border-[#B3224D]/30 rounded-xl p-6">
              <div class="flex items-center gap-3 mb-6">
                <Calendar class="w-5 h-5 text-[#B3224D]" />
                <h2 class="text-xl font-bold text-white">Información del Evento</h2>
              </div>
              
              <div class="space-y-4">
                <div>
                  <p class="text-sm text-gray-400 mb-1">Nombre del Evento</p>
                  <p class="text-lg font-semibold text-white">{{ estadisticas.evento.nombre }}</p>
                </div>
                
                <div>
                  <p class="text-sm text-gray-400 mb-1">Fecha</p>
                  <p class="text-lg font-semibold text-white">{{ formatDate(estadisticas.evento.fecha) }}</p>
                </div>
                
                <div v-if="estadisticas.evento.lugar">
                  <p class="text-sm text-gray-400 mb-1">Lugar</p>
                  <p class="text-lg font-semibold text-white">{{ estadisticas.evento.lugar }}</p>
                </div>
                
                <div>
                  <p class="text-sm text-gray-400 mb-1">Estado</p>
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                        :class="{
                          'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30': estadisticas.evento.estado === 'Próximo',
                          'bg-green-500/20 text-green-300 border border-green-500/30': estadisticas.evento.estado === 'Activo',
                          'bg-gray-500/20 text-gray-300 border border-gray-500/30': estadisticas.evento.estado === 'Finalizado'
                        }">
                    {{ estadisticas.evento.estado }}
                  </span>
                </div>

                <div class="pt-4 border-t border-gray-700">
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-gray-400">Promedio por Venta</span>
                    <span class="text-lg font-bold text-white">S/ {{ formatNumber(estadisticas.ventas.promedio_venta) }}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  </AdmLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { eventosService } from '@/services/eventosService'
import AdmLayout from '@/Layouts/AdmLayout.vue'
import { 
  ShoppingCart, 
  DollarSign, 
  Ticket, 
  TrendingUp, 
  MapPin, 
  CreditCard, 
  BarChart3,
  CheckCircle,
  XCircle,
  Calendar
} from 'lucide-vue-next'

const eventos = ref([])
const eventoSeleccionado = ref('')
const estadisticas = ref(null)
const cargando = ref(false)

onMounted(async () => {
  await cargarEventos()
})

const cargarEventos = async () => {
  try {
    const response = await eventosService.getEventos(1, 100)
    eventos.value = response.results || response
  } catch (error) {
    console.error('Error al cargar eventos:', error)
  }
}

const cargarEstadisticas = async () => {
  if (!eventoSeleccionado.value) {
    estadisticas.value = null
    return
  }
  
  cargando.value = true
  try {
    estadisticas.value = await eventosService.getEstadisticasEvento(eventoSeleccionado.value)
  } catch (error) {
    console.error('Error al cargar estadísticas:', error)
  } finally {
    cargando.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-PE', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatNumber = (number) => {
  return new Intl.NumberFormat('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(number)
}

const calcularPorcentaje = (valor, total) => {
  if (total === 0) return 0
  return ((valor / total) * 100).toFixed(1)
}
</script>
