<script setup>
import { ref } from "vue";
import ToastNotification from "@/components/ToastNotification.vue";
import InputLabel from "@/components/Inputs/InputLabel.vue";
import InputText from "@/components/Inputs/InputText.vue";
import InputError from "@/components/Inputs/InputError.vue";
import InputImage from "@/components/Inputs/InputImage.vue";
import DialogModal from "@/components/DialogModal.vue";
import ButtonCancel from "@/components/Buttons/ButtonCancel.vue";
import ButtonSave from "@/components/Buttons/ButtonSave.vue";
import { useToasts } from "@/Helpers/useToasts";
import { useCategoriasStore } from "@/stores/categorias";

const emit = defineEmits(["close", "data_created"]);
const props = defineProps({ show: Boolean });

const categoriasStore = useCategoriasStore();

function getFormData() {
	return {
		nombre: "",
		imagen_path: null,
		estado: 1,
		activo: true,
	};
}

const form = ref(getFormData());
const imagenError = ref(null);

function onImageError(val) {
	if (imagenError && typeof imagenError.value !== 'undefined') {
		imagenError.value = val && val.length ? val[0] : null;
	}
}

function onImageCleared() {
	if (imagenError && typeof imagenError.value !== 'undefined') {
		imagenError.value = null;
	}
}

const errors = ref({});
const toastForm = ref(null);
const toastGlobal = ref(null);
const toastFormHelper = useToasts(toastForm);
const toastGlobalHelper = useToasts(toastGlobal);
const cargando = ref(false);

const closeModal = () => {
	emit("close");
	limpiar();
};

const limpiar = () => {
	form.value = getFormData();
	errors.value = {};
	imagenError.value = null;
};

const crearData = async () => {
	cargando.value = true;
	errors.value = {};
	imagenError.value = null;
	try {
		const data = new FormData();
		data.append("nombre", form.value.nombre);
		if (form.value.imagen_path) data.append("imagen_path", form.value.imagen_path);
		data.append("estado", form.value.estado);
		data.append("activo", form.value.activo);
		await categoriasStore.createCategoria(data);
		toastGlobalHelper.success("Categoría creada exitosamente");
		emit("data_created");
		closeModal();
	} catch (error) {
		if (error.response?.data) {
			errors.value = error.response.data;
			toastFormHelper.error(error.response.data.message || "Error al crear la categoría");
		} else {
			toastFormHelper.error("Error al crear la categoría");
		}
	} finally {
		cargando.value = false;
	}
};
</script>

<template>
	<DialogModal :show="show" @close="closeModal" >
		<template #title>
			<span>Agregar Categoría</span>
		</template>
		<template #content>
			<form @submit.prevent="crearData" class="space-y-4">
				<div>
					<InputLabel value="Nombre" />
					<InputText v-model="form.nombre" type="text" />
					<InputError :message="errors.nombre" />
				</div>
				<div>
					<InputLabel value="Imagen" />
					<InputImage
						v-model="form.imagen_path"
						:previewImage="null"
						:maxSizeMb="2"
						:accept="['image/jpeg','image/png','image/webp']"
						@error="onImageError"
						@cleared="onImageCleared"
					/>
					<InputError :message="imagenError || errors.imagen_path" />
				</div>
			</form>
		</template>
		<template #footer>
			<div class="flex justify-end space-x-2">
				<ButtonCancel @click="closeModal" :disabled="cargando">Cancelar</ButtonCancel>
				<ButtonSave @click="crearData" :loading="cargando">Guardar</ButtonSave>
			</div>
		</template>
		<ToastNotification ref="toastForm" position="top-right" />
	</DialogModal>
</template>
