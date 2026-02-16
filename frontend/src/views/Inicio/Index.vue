<script setup>
import AppLayout from "@/Layouts/AppLayout.vue";
import Bienvenido from "./Partes/Bienvenido.vue";
import Caracteristicas from "./Partes/Caracteristicas.vue";
import EventosDestacados from "./Partes/EventosDestacados.vue";
import Categorias from "./Partes/Categorias.vue";
import LlamadoAccion from "./Partes/LlamadoAccion.vue";
import { ref, onMounted } from 'vue';

const estadisticas = ref({
    eventosActivos: 0,
    ticketsVendidos: 0,
    usuariosRegistrados: 0
});

onMounted(() => {
    // Aquí puedes cargar las estadísticas desde tu API
    estadisticas.value = {
        eventosActivos: 25,
        ticketsVendidos: 1250,
        usuariosRegistrados: 850
    };
});
</script>

<template>
    <AppLayout title="Inicio">
        <Bienvenido />
        
        <Caracteristicas />
        
        <Categorias />
        
        <EventosDestacados />
        
        <LlamadoAccion :estadisticas="estadisticas" />
    </AppLayout>
</template>
