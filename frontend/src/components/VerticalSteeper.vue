<template>
  <div class="w-full bg-white rounded-[20px] shadow p-5 mt-6 flex flex-col h-full">

    <div class="flex h-full">
      <!-- Steps siempre verticales -->
      <div class="w-20 md:w-64 relative flex-col flex">
        <!-- Línea gris -->
        <div class="absolute left-[18px] top-0 bottom-0 w-[4px] bg-gray-300 rounded-full"></div>

        <!-- Línea progreso -->
        <div
          class="absolute left-[18px] top-0 w-[4px] bg-[#B3224D] rounded-full transition-all duration-500"
          :style="{ height: progressHeight }"
        ></div>

        <!-- Steps -->
        <div class="flex flex-col justify-between h-full relative z-10">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="flex items-center cursor-pointer relative"
            @click="goToStep(index)"
          >
            <!-- Círculo -->
            <div
              class="flex items-center justify-center w-10 h-10 rounded-full border-4 font-bold transition relative z-10 shadow-lg text-lg"
              :class="{
                'bg-[#B3224D] text-white border-white': currentStep === index,
                'bg-white text-[#B3224D] border-[#B3224D]': currentStep !== index
              }"
            >
              {{ index + 1 }}
            </div>

            <!-- Texto oculto en móvil -->
            <span
              class="ml-3 font-semibold hidden md:inline"
              :class="{
                'text-[#B3224D]': currentStep === index,
                'text-gray-800': currentStep !== index
              }"
            >
              {{ step }}
            </span>
          </div>
        </div>
      </div>

      <!-- Contenido -->
      <div class="flex-1 pl-4 md:pl-12 flex flex-col">
        <div class="flex-1 min-h-[300px]">
          <slot :name="`step-${currentStep}`"></slot>
        </div>

        <!-- Navegación -->
        <div class="flex justify-between mt-6">
          <BaseButton
            v-if="currentStep > 0"
            variant="secondary"
            @click="prevStep"
          >
            ← Anterior
          </BaseButton>

          <BaseButton
            v-if="currentStep < steps.length - 1"
            variant="primary"
            class="ml-auto"
            @click="nextStep"
          >
            Siguiente →
          </BaseButton>

          <BaseButton
            v-else
            variant="primary"
            class="ml-auto"
            :disabled="props.isSubmitting"
            @click="$emit('finish')"
          >
            <span v-if="props.isSubmitting" class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ props.finishSubmittingText }}
            </span>
            <span v-else>{{ finishButtonText }}</span>
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import BaseButton from "@/ui/components/button/button.vue"

const props = defineProps({
  steps: { type: Array, required: true },
  validateStep: { type: Function, default: null },
  finishButtonText: { type: String, default: 'Finalizar' },
  isSubmitting: { type: Boolean, default: false },
  finishSubmittingText: { type: String, default: 'Enviando...' }
})

const emit = defineEmits(['finish', 'step-change'])

const currentStep = ref(0)

const nextStep = async () => {
  // Validar antes de avanzar si hay función de validación
  if (props.validateStep) {
    const isValid = await props.validateStep(currentStep.value)
    if (!isValid) return
  }
  
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
    emit('step-change', currentStep.value)
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
    emit('step-change', currentStep.value)
  }
}

const goToStep = (index) => {
  currentStep.value = index
  emit('step-change', currentStep.value)
}

const progressHeight = computed(() => {
  if (props.steps.length <= 1) return "0%"
  return `${(currentStep.value / (props.steps.length - 1)) * 100}%`
})

const reset = () => {
  currentStep.value = 0
}

defineExpose({ reset, currentStep })
</script>
