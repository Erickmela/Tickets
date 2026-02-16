<script setup>
import { computed } from 'vue';

const props = defineProps({
    estado: {
        type: [String, Number, Boolean],
        required: true
    },
    status: {
        type: [String, Number, Boolean],
        required: false
    }
});

const isActive = computed(() => {
    const value = props.estado !== undefined ? props.estado : props.status;
    
    // Si es booleano, usarlo directamente
    if (typeof value === 'boolean') {
        return value;
    }
    
    // Si es número: 1 = activo, 2 = inactivo
    if (typeof value === 'number') {
        return value === 1;
    }
    
    // Si es string, intentar convertir
    if (value === 'true' || value === '1') return true;
    if (value === 'false' || value === '2') return false;
    
    return null;
});
</script>
<template>
    <span v-if="isActive === true" class="px-2 py-1 text-xs font-medium rounded-full bg-green-700 text-white">Activo</span>
    <span v-else-if="isActive === false" class="px-2 py-1 text-xs font-medium rounded-full bg-red-700 text-white">Inactivo</span>
    <span v-else class="px-2 py-1 text-xs font-medium rounded-full bg-orange-700 text-white">Indefinido</span>
</template>
