<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="buttonClasses"
    class="px-6 py-3 rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'tertiary'].includes(value)
  },
  type: {
    type: String,
    default: 'button'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const buttonClasses = computed(() => {
  const variants = {
    primary: 'bg-[#B3224D] text-white hover:bg-[#8d1a3c] active:bg-[#6e1530]',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 active:bg-gray-400',
    tertiary: 'bg-transparent text-[#B3224D] border-2 border-[#B3224D] hover:bg-[#B3224D] hover:text-white'
  }
  
  return variants[props.variant] || variants.primary
})
</script>
