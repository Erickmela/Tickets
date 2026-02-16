<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import _ from 'lodash'
import axios from 'axios'

const debounce = _.debounce

const props = defineProps({
    modelValue: { type: [Array, String, Number, Object], default: () => [] },
    multiple: { type: Boolean, default: false },
    fetchUrl: { type: String, required: true },
    getLabel: { type: Function, required: true },
    valueKey: { type: String, default: 'id' },
    placeholder: { type: String, default: 'Seleccione…' },
    debounceMs: { type: Number, default: 400 },
    preload: { type: Boolean, default: true },
    optionsInitial: { type: Array, default: () => [] },
    disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])
const open = ref(false)
const loading = ref(false)
const search = ref('')
const options = ref([])
const selectedIds = ref([])
const selectedMap = ref({})

// Referencias para el posicionamiento dinámico
const root = ref(null)
const dropdown = ref(null)
const dropdownPosition = ref('bottom') // 'bottom' o 'top'

/* ---------- helpers ---------- */
const key = props.valueKey
const uniqById = (arr) => Object.values(arr.reduce((acc, o) => {
    acc[o[key]] = o; return acc
}, {}))

/* ---------- init ---------- */
onMounted(() => {
    // 1) v‑model
    if (props.multiple) selectedIds.value = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    else if (props.modelValue !== null && props.modelValue !== undefined) selectedIds.value = [props.modelValue]

    // 2) cache inicial
    props.optionsInitial.forEach(o => selectedMap.value[o[key]] = o)

    // 3) primer fetch
    if (props.preload) fetchOptions()
})

/* ---------- Función para calcular la posición del dropdown ---------- */
const calculateDropdownPosition = async () => {
    await nextTick()

    if (!root.value || !dropdown.value) return

    const triggerRect = root.value.getBoundingClientRect()
    const dropdownHeight = 280 // altura máxima estimada del dropdown (max-h-60 + padding)
    const viewportHeight = window.innerHeight
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop

    // Espacio disponible debajo del trigger
    const spaceBelow = viewportHeight - triggerRect.bottom
    // Espacio disponible arriba del trigger
    const spaceAbove = triggerRect.top

    // Decidir posición basada en espacio disponible
    if (spaceBelow >= dropdownHeight || spaceBelow >= spaceAbove) {
        dropdownPosition.value = 'bottom'
    } else {
        dropdownPosition.value = 'top'
    }
}

/* ---------- emitir cambios ---------- */
watch(selectedIds, () => {
    if (props.multiple) emit('update:modelValue', selectedIds.value)
    else { emit('update:modelValue', selectedIds.value[0] ?? null); open.value = false }
})

/* ---------- watch open state ---------- */
watch(open, async (newValue) => {
    if (newValue) {
        await calculateDropdownPosition()
    }
})

/* ---------- fetch datos ---------- */
const fetchOptions = async (q = '') => {
    try {
        loading.value = true
        const { data } = await axios.get(props.fetchUrl, { params: { search: q } })
        const backend = Array.isArray(data) ? data : []

        const merged = uniqById([
            ...Object.values(selectedMap.value),
            ...backend,
        ])

        options.value = merged.sort((a, b) => {
            const ia = selectedIds.value.includes(a[key]) ? 0 : 1
            const ib = selectedIds.value.includes(b[key]) ? 0 : 1
            return ia - ib
        })
    } catch (e) {
        console.error('AsyncSelect fetch error', e)
    } finally { loading.value = false }
}

const handleSearch = debounce(() => fetchOptions(search.value), props.debounceMs)

/* ---------- texto del trigger ---------- */
const displayText = computed(() => {
    if (selectedIds.value.length === 0) return props.placeholder
    if (!props.multiple) {
        const opt = selectedMap.value[selectedIds.value[0]] || options.value.find(o => o[key] === selectedIds.value[0])
        return opt ? props.getLabel(opt) : 'Seleccione…'
    }
    return `${selectedIds.value.length} seleccionado(s)`
})

/* ---------- selección ---------- */
const isChecked = id => selectedIds.value.includes(id)

const toggle = (opt) => {
    const id = opt[key]
    selectedMap.value[id] = opt

    if (props.multiple) {
        const i = selectedIds.value.indexOf(id)
        i === -1 ? selectedIds.value.push(id) : selectedIds.value.splice(i, 1)
    } else selectedIds.value = [id]

    options.value = uniqById([...Object.values(selectedMap.value), ...options.value])
        .sort((a, b) => (isChecked(a[key]) ? 0 : 1) - (isChecked(b[key]) ? 0 : 1))
}

/* ---------- cerrar al hacer clic fuera ---------- */
const onClickOutside = e => {
    if (root.value && !root.value.contains(e.target)) open.value = false
}

onMounted(() => {
    document.addEventListener('click', onClickOutside)
    window.addEventListener('resize', calculateDropdownPosition)
    window.addEventListener('scroll', calculateDropdownPosition)
})

onUnmounted(() => {
    document.removeEventListener('click', onClickOutside)
    window.removeEventListener('resize', calculateDropdownPosition)
    window.removeEventListener('scroll', calculateDropdownPosition)
})

/* ---------- clases dinámicas para el dropdown ---------- */
const dropdownClasses = computed(() => {
    const baseClasses = "absolute z-50 w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-sm shadow-lg"

    if (dropdownPosition.value === 'top') {
        return `${baseClasses} bottom-full mb-1`
    } else {
        return `${baseClasses} top-full mt-1`
    }
})
</script>

<template>
    <div ref="root" class="relative">
        <!-- disparador -->
        <div @click="!props.disabled && (open = !open)" class="w-full p-3 bg-white dark:bg-gray-800 dark:text-white border border-gray-300 dark:border-gray-600 rounded-sm shadow-sm
             flex justify-between items-center cursor-pointer" :class="{ 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-gray-900': props.disabled }">
            <span :class="{ 'text-gray-500 dark:text-white': selectedIds.length === 0 }" class="truncate">{{
                displayText }}</span>
            <svg v-if="!props.disabled" class="w-4 h-4 ml-2 text-gray-500 dark:text-gray-500 transition-transform" :class="{ 'rotate-180': open }" fill="none"
                viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
        </div>

        <!-- dropdown con posicionamiento dinámico -->
        <div v-show="open" ref="dropdown" :class="dropdownClasses">
            <div class="p-2 border-b border-gray-200 dark:border-gray-700">
                <input v-model="search" @input="handleSearch" type="text" placeholder="Buscar…"
                    class="w-full p-2 text-sm text-gray-300 dark:text-white bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded focus:ring-prim focus:border-prim" />
            </div>

            <div class="max-h-40 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-700">
                <div v-if="loading" class="p-3 text-sm text-center text-gray-500 dark:text-white">Cargando…</div>
                <div v-else-if="options.length === 0" class="p-3 text-sm text-center text-gray-500 dark:text-white">Sin
                    resultados</div>

                <div v-else v-for="opt in options" :key="opt[key]" @click="toggle(opt)"
                    class="w-full flex items-center px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                    <input :type="props.multiple ? 'checkbox' : 'radio'" :checked="isChecked(opt[key])"
                        class="text-prim w-4 h-4 border-gray-300 rounded focus:ring-prim" />
                    <span class="ml-2 text-sm truncate text-gray-700 dark:text-white">{{ props.getLabel(opt) }}</span>
                </div>
            </div>
        </div>
    </div>
</template>
