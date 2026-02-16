<script setup>
const props = defineProps({
    modelValue: {
        type: [String, Number, Boolean],
        required: true,
    },
    name: {
        type: String,
        default: "estado",
    },
    option1Value: {
        type: [String, Number, Boolean],
        default: 1,
    },
    option2Value: {
        type: [String, Number, Boolean],
        default: 2,
    },
});

const emit = defineEmits(["update:modelValue"]);

const updateValue = (value) => {
    emit("update:modelValue", value);
};
</script>

<template>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <!-- Opción 1 -->
        <label
            class="relative flex items-center p-3 bg-white dark:bg-gray-800 border cursor-pointer rounded-sm shadow-sm outline-none"
            :class="
                modelValue == option1Value
                    ? 'border-prim bg-orange-50 dark:bg-orange-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-prim/50'
            "
        >
            <input
                type="radio"
                :name="name"
                :checked="modelValue == option1Value"
                @change="updateValue(option1Value)"
                class="w-4 h-4 text-prim border-gray-300 focus:ring-prim dark:border-gray-600 dark:bg-gray-700"
            />
            <div class="ml-3 flex items-center w-full">
                <slot name="option1">
                    <span class="text-sm font-medium"
                        :class="
                            modelValue == option1Value
                                ? 'text-prim dark:text-orange-400'
                                : 'text-gray-700 dark:text-gray-300'
                        "
                    >
                        Opción 1
                    </span>
                </slot>
            </div>
        </label>

        <!-- Opción 2 -->
        <label
            class="relative flex items-center p-3 bg-white dark:bg-gray-800 border cursor-pointer rounded-sm shadow-sm outline-none"
            :class="
                modelValue == option2Value
                    ? 'border-prim bg-orange-50 dark:bg-orange-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-prim/50'
            "
        >
            <input
                type="radio"
                :name="name"
                :checked="modelValue == option2Value"
                @change="updateValue(option2Value)"
                class="w-4 h-4 text-prim border-gray-300 focus:ring-prim dark:border-gray-600 dark:bg-gray-700"
            />
            <div class="ml-3 flex items-center w-full">
                <slot name="option2">
                    <span class="text-sm font-medium"
                        :class="
                            modelValue == option2Value
                                ? 'text-prim dark:text-orange-400'
                                : 'text-gray-700 dark:text-gray-300'
                        "
                    >
                        Opción 2
                    </span>
                </slot>
            </div>
        </label>
    </div>
</template>
