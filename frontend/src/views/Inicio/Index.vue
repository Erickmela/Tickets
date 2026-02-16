<script setup>
import AppLayout from "@/Layouts/AppLayout.vue";
import Bienvenido from "./Partes/Bienvenido.vue";
import CarouselEventos from "./Partes/CarouselEventos.vue";
import Caracteristicas from "./Partes/Caracteristicas.vue";
import EventosNuevos from "./Partes/EventosNuevos.vue";
import Categorias from "./Partes/Categorias.vue";
import EventosDestacados from "./Partes/EventosDestacados.vue";
import LlamadoAccion from "./Partes/LlamadoAccion.vue";
import { ref, onMounted } from 'vue';
import { eventosService } from '@/services/eventosService';
import { usuariosService } from '@/services/usuariosService';

const estadisticas = ref({
    eventosActivos: 0,
    ticketsVendidos: 0,
    usuariosRegistrados: 0
});
const loading = ref(true);

onMounted(async () => {
    try {
        // Cargar eventos activos
        try {
            const eventosData = await eventosService.getEventosActivos();
            estadisticas.value.eventosActivos = eventosData.length || 0;
            
            // Calcular tickets vendidos de todos los eventos activos
            let totalTickets = 0;
            for (const evento of eventosData) {
                try {
                    const stats = await eventosService.getEstadisticasEvento(evento.id);
                    totalTickets += stats.tickets?.total_vendidos || 0;
                } catch (error) {
                    // Estadísticas no disponibles para este evento
                    console.debug('Estadísticas no disponibles para el evento:', evento.id);
                }
            }
            estadisticas.value.ticketsVendidos = totalTickets;
        } catch (error) {
            console.debug('Eventos no disponibles:', error.message);
            estadisticas.value.eventosActivos = 0;
            estadisticas.value.ticketsVendidos = 0;
        }
        
        // Cargar usuarios (requiere autenticación)
        try {
            const usuariosData = await usuariosService.getUsuarios(1, 1);
            estadisticas.value.usuariosRegistrados = usuariosData.count || 0;
        } catch (error) {
            // Usuario no autenticado o sin permisos
            estadisticas.value.usuariosRegistrados = 0;
        }
    } catch (error) {
        console.error('Error general cargando estadísticas:', error);
    } finally {
        loading.value = false;
    }
});
</script>

<template>
    <AppLayout title="Inicio">
        <Bienvenido />
        
        <CarouselEventos />
        
        <Caracteristicas />
        
        <EventosNuevos :n_eventos="8" />
        
        <Categorias />

        <EventosDestacados />
        
        <LlamadoAccion :estadisticas="estadisticas" />
    </AppLayout>
</template>
