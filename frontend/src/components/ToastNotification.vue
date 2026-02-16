<script setup>
import { ref, reactive } from "vue";
import { CheckCircle, XCircle, AlertTriangle, Info, X } from "lucide-vue-next";

const toasts = ref([]);
const nextId = ref(1);

const positions = ["top", "bottom"];

const progressBarClasses = {
    success: "bg-green-300",
    error: "bg-red-300",
    warning: "bg-yellow-300",
    info: "bg-blue-300",
};

function addToast({
    type = "info",
    title = "",
    message = "",
    position = "top",
    duration = 3000,
}) {
    const id = nextId.value++;
    const toast = reactive({
        id,
        type,
        title,
        message,
        position,
        duration,
        progress: 100,
    });

    toasts.value.push(toast);

    if (duration > 0) {
        const interval = 50;
        const steps = duration / interval;
        const decrement = 100 / steps;

        const timer = setInterval(() => {
            toast.progress -= decrement;
            if (toast.progress <= 0) {
                clearInterval(timer);
                removeToast(id);
            }
        }, interval);
    }
}

function removeToast(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
}

defineExpose({ addToast });
</script>

<template>
    <div>
        <!-- Una transición por posición -->
        <template v-for="position in positions" :key="position">
            <transition-group name="toast" tag="div" :class="[
                'fixed z-[9999] space-y-4 w-full max-w-sm px-4 pointer-events-none',
                position === 'top' ? 'top-4 right-2' : 'bottom-4 right-2',
            ]">
                <div v-for="toast in toasts.filter(
                    (t) => t.position === position
                )" :key="toast.id" :class="[
                        'relative flex items-start p-4 rounded-xl shadow-lg text-white overflow-hidden border-l-4 pointer-events-auto cursor-pointer',
                        toast.type === 'success' &&
                        'bg-green-500 border-green-600',
                        toast.type === 'error' && 'bg-red-500 border-red-600',
                        toast.type === 'warning' &&
                        'bg-yellow-500 border-yellow-600 text-gray-900',
                        toast.type === 'info' && 'bg-blue-500 border-blue-600',
                    ]" @click="removeToast(toast.id)">
                    <!-- Icon -->
                    <div class="mt-1 mr-3">
                        <component :is="toast.type === 'success'
                                ? CheckCircle
                                : toast.type === 'error'
                                    ? XCircle
                                    : toast.type === 'warning'
                                        ? AlertTriangle
                                        : Info
                            " class="w-5 h-5" :class="toast.type === 'warning'
                                    ? 'text-yellow-800'
                                    : 'text-white'
                                " />
                    </div>

                    <!-- Content -->
                    <div class="flex-1">
                        <p class="font-semibold leading-tight">
                            {{ toast.title }}
                        </p>
                        <p class="text-sm mt-1 opacity-90">
                            {{ toast.message }}
                        </p>
                    </div>

                    <!-- Close -->
                    <button @click.stop="removeToast(toast.id)" class="ml-3 mt-1 opacity-70 hover:opacity-100">
                        <X class="w-4 h-4" />
                    </button>

                    <!-- Progress bar -->
                    <div v-if="toast.duration > 0" class="absolute bottom-0 left-0 h-1"
                        :class="progressBarClasses[toast.type]" :style="{
                            width: toast.progress + '%',
                            transition: 'width 50ms linear',
                        }"></div>
                </div>
            </transition-group>
        </template>
    </div>
</template>

<style>
.toast-enter-active,
.toast-leave-active {
    transition: all 0.4s ease;
}

.toast-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

.toast-leave-to {
    opacity: 0;
    transform: translateY(20px);
}

.toast-move {
    transition: transform 0.4s ease;
}
</style>
