<script setup>
import AppLayout from "@/Layouts/AppLayout.vue";
import Bienvenido from "./Partes/Bienvenido.vue";
import CarouselEventos from "./Partes/CarouselEventos.vue";
import Caracteristicas from "./Partes/Caracteristicas.vue";
import EventosNuevos from "./Partes/EventosNuevos.vue";
import Categorias from "./Partes/Categorias.vue";
import LlamadoAccion from "./Partes/LlamadoAccion.vue";
</script>

<template>
    <AppLayout title="Inicio">
        <Bienvenido />
        
        <CarouselEventos />
        
        <Caracteristicas />
        
        <EventosNuevos :n_eventos="8" />
        
        <Categorias />
        
        <LlamadoAccion />
    </AppLayout>
</template>
