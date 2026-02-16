<script setup>
import { Ticket, Smartphone, Shield, Zap, CreditCard, CalendarDays } from 'lucide-vue-next';

const caracteristicas = [
    {
        icono: Ticket,
        titulo: 'Tickets Únicos',
        descripcion: 'Cada ticket tiene un código UUID único e imposible de clonar, garantizando tu entrada al evento.',
        color: 'from-[#B3224D] to-[#8d1a3c]'
    },
    {
        icono: Smartphone,
        titulo: 'Validación QR',
        descripcion: 'Sistema de validación instantánea mediante código QR. Control de acceso en tiempo real.',
        color: 'from-[#B3224D] to-[#8d1a3c]'
    },
    {
        icono: Shield,
        titulo: '100% Seguro',
        descripcion: 'Protección anti-clonación garantizada. Tus tickets están seguros desde la compra hasta el ingreso.',
        color: 'from-[#B3224D] to-[#8d1a3c]'
    },
    {
        icono: Zap,
        titulo: 'Compra Rápida',
        descripcion: 'Proceso de compra simple y rápido. Obtén tus tickets en minutos.',
        color: 'from-[#B3224D] to-[#8d1a3c]'
    },
    {
        icono: CreditCard,
        titulo: 'Pago Seguro',
        descripcion: 'Múltiples métodos de pago seguros. Transacciones protegidas.',
        color: 'from-[#B3224D] to-[#8d1a3c]'
    },
    {
        icono: CalendarDays,
        titulo: 'Variedad de Eventos',
        descripcion: 'Conciertos, deportes, teatro, conferencias y mucho más en un solo lugar.',
        color: 'from-[#B3224D] to-[#8d1a3c]'
    }
];

</script>

<template>
    <section class="py-20 bg-gray-50 dark:bg-gray-800">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <div class="inline-block mb-4">
                    <span class="text-[#B3224D] font-bold text-sm uppercase tracking-wider">Beneficios</span>
                </div>
                <h2 class="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                    ¿Por qué elegirnos?
                </h2>
                <p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                    La mejor experiencia en compra de tickets con seguridad garantizada
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div 
                    v-for="(caracteristica, index) in caracteristicas" 
                    :key="index"
                    class="group relative bg-white dark:bg-gray-900 rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2"
                >
                    <!-- Borde decorativo con gradiente -->
                    <div class="absolute inset-0 rounded-3xl bg-gradient-to-br opacity-0 group-hover:opacity-10 transition-opacity duration-300" 
                         :class="caracteristica.color"></div>
                    
                    <!-- Icono con efecto de escala -->
                    <div class="mb-6 transform group-hover:scale-110 transition-transform duration-300">
                        <component 
                            :is="caracteristica.icono" 
                            :size="56" 
                            :stroke-width="1.5"
                            class="text-[#B3224D] group-hover:text-[#8d1a3c] transition-colors"
                        />
                    </div>
                    
                    <!-- Título con color del tema -->
                    <h3 class="text-xl font-bold mb-3 text-gray-900 dark:text-white group-hover:text-[#B3224D] transition-colors">
                        {{ caracteristica.titulo }}
                    </h3>
                    
                    <!-- Descripción -->
                    <p class="text-gray-600 dark:text-gray-300 leading-relaxed">
                        {{ caracteristica.descripcion }}
                    </p>
                    
                    <!-- Punto decorativo -->
                    <div class="absolute top-8 right-8 w-2 h-2 rounded-full bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                         :class="caracteristica.color"></div>
                </div>
            </div>
        </div>
    </section>
</template>
