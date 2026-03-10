import { ref, computed } from 'vue';

// Clave para localStorage
const CART_STORAGE_KEY = 'tickets_carrito';

// Estado reactivo del carrito
const cartItems = ref([]);

// Cargar carrito desde localStorage al iniciar
function loadCartFromStorage() {
    try {
        const stored = localStorage.getItem(CART_STORAGE_KEY);
        if (stored) {
            cartItems.value = JSON.parse(stored);
        }
    } catch (error) {
        console.error('Error cargando carrito desde localStorage:', error);
        cartItems.value = [];
    }
}

// Guardar carrito en localStorage
function saveCartToStorage() {
    try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems.value));
    } catch (error) {
        console.error('Error guardando carrito en localStorage:', error);
    }
}

// Contador de items en el carrito (número de presentaciones diferentes)
export const cartCount = computed(() => {
    return cartItems.value.length;
});

// Obtener todos los items del carrito
export function getCartItems() {
    return cartItems.value;
}

// Agregar item al carrito
export function addToCart(evento, presentacion, zonasSeleccionadas) {
    // Buscar si ya existe el item con la misma presentación
    const existingItemIndex = cartItems.value.findIndex(
        item => item.eventoId === evento.id && item.presentacionId === presentacion.id
    );

    if (existingItemIndex !== -1) {
        // Si existe, actualizar las zonas
        const existingItem = cartItems.value[existingItemIndex];
        zonasSeleccionadas.forEach(nuevaZona => {
            const zonaExistente = existingItem.zonas.find(z => z.id === nuevaZona.id);
            if (zonaExistente) {
                zonaExistente.cantidad += nuevaZona.cantidad;
            } else {
                existingItem.zonas.push(nuevaZona);
            }
        });
    } else {
        // Si no existe, agregar nuevo item
        cartItems.value.push({
            eventoId: evento.id,
            eventoNombre: evento.nombre,
            eventoImagen: evento.imagen_principal,
            comision_porcentaje: evento.comision_porcentaje || 0,
            comision_incluida_precio: evento.comision_incluida_precio || false,
            presentacionId: presentacion.id,
            presentacionFecha: presentacion.fecha,
            presentacionHora: presentacion.hora_inicio,
            zonas: zonasSeleccionadas.map(z => ({ ...z }))
        });
    }

    saveCartToStorage();
}

// Eliminar item del carrito
export function removeFromCart(eventoId, presentacionId) {
    cartItems.value = cartItems.value.filter(
        item => !(item.eventoId === eventoId && item.presentacionId === presentacionId)
    );
    saveCartToStorage();
}

// Actualizar cantidad de una zona específica
export function updateZonaCantidad(eventoId, presentacionId, zonaId, cantidad) {
    const item = cartItems.value.find(
        item => item.eventoId === eventoId && item.presentacionId === presentacionId
    );
    
    if (item) {
        const zona = item.zonas.find(z => z.id === zonaId);
        if (zona) {
            if (cantidad <= 0) {
                // Eliminar la zona si la cantidad es 0
                item.zonas = item.zonas.filter(z => z.id !== zonaId);
                // Si no quedan zonas, eliminar el item completo
                if (item.zonas.length === 0) {
                    removeFromCart(eventoId, presentacionId);
                    return;
                }
            } else {
                zona.cantidad = cantidad;
            }
        }
        saveCartToStorage();
    }
}

// Limpiar todo el carrito
export function clearCart() {
    cartItems.value = [];
    localStorage.removeItem(CART_STORAGE_KEY);
}

// Calcular precio total del carrito
export function getCartTotal() {
    return cartItems.value.reduce((total, item) => {
        return total + item.zonas.reduce((sum, zona) => {
            return sum + (zona.precio * zona.cantidad);
        }, 0);
    }, 0);
}

// Inicializar carrito al cargar el módulo
loadCartFromStorage();

// Legacy functions para compatibilidad
export function setCartCount(count) {
    // Esta función ya no es necesaria con el computed, pero la mantenemos por compatibilidad
    console.warn('setCartCount is deprecated, cart count is now computed automatically');
}

export function incrementCartCount() {
    console.warn('incrementCartCount is deprecated, use addToCart instead');
}

export function decrementCartCount() {
    console.warn('decrementCartCount is deprecated, use removeFromCart instead');
}
