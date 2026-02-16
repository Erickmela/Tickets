<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
    x: Number,
    y: Number,
    show: Boolean
})

const emit = defineEmits(['close'])

const dropdownRef = ref(null)

function handleClickOutside(event) {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
        emit('close')
    }
}

function handleScroll() {
    emit('close')
}

onMounted(() => {
    document.addEventListener('mousedown', handleClickOutside)
    window.addEventListener('scroll', handleScroll, true)
})

onBeforeUnmount(() => {
    document.removeEventListener('mousedown', handleClickOutside)
    window.removeEventListener('scroll', handleScroll, true)
})
</script>

<template>
    <transition name="fade">
        <div v-if="show" ref="dropdownRef" class="fixed z-50" :style="{
            top: (y - 20) + 'px',
            left: (x - 5) + 'px',
            transform: 'translateX(-100%)'
        }">
            <div class=" bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg shadow-lg">
                <div class="p-2 space-y-1 text-sm">
                    <slot />
                </div>
            </div>
        </div>
    </transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
