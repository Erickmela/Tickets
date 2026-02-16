import axios from 'axios';
import { setCartCount } from "@/Helpers/cartState";
axios.defaults.withCredentials = true;

export async function agregarCursoAlCarrito(cur_id) {
    try {
        const response = await axios.post(route('carrito.store'), {
            cur_id: cur_id
        });

        if (response.data.success) {
            if (response.data.count !== undefined) {
                setCartCount(response.data.count);
            }
            return { success: true, message: response.data.message };
        } else {
            console.error(response.data.message);
            return { success: false, message: response.data.message };
        }
    } catch (error) {
        let message = 'Error desconocido al agregar el curso.';
        if (error.response && error.response.data && error.response.data.message) {
            message = error.response.data.message;
        }
        return { success: false, message: message };
    }
}
