// Permisos por rol
const PERMISOS = {
    ADMIN: ['crear_ventas', 'anular_ventas', 'ver_reportes', 'gestionar_eventos', 'gestionar_usuarios'],
    VENDEDOR: ['crear_ventas', 'ver_reportes'],
    VALIDADOR: ['validar_tickets'],
};

/**
 * Verifica si un rol tiene un permiso específico
 */
export function hasPermission(permiso, rol) {
    if (!rol || !PERMISOS[rol]) return false;
    return PERMISOS[rol].includes(permiso);
}

/**
 * Formatea un precio en soles peruanos
 */
export function formatPrice(precio) {
    if (precio === null || precio === undefined) return 'S/ 0.00';
    return new Intl.NumberFormat('es-PE', {
        style: 'currency',
        currency: 'PEN',
        minimumFractionDigits: 2,
    }).format(precio);
}

/**
 * Formatea un precio (alias simplificado)
 */
export function formatPrecio(precio) {
    if (!precio || precio === "0.00") return "Gratis";
    return `S/ ${parseFloat(precio).toFixed(2)}`;
}

/**
 * Formatea una fecha a texto legible con hora
 */
export function dateTimeText(fecha) {
    if (!fecha) return 'N/A';
    const date = new Date(fecha);
    return new Intl.DateTimeFormat('es-PE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

/**
 * Formatea una fecha a texto largo
 */
export function dateText(date) {
    if (!date) return "";
    // Agregar 'T00:00:00' para forzar interpretación como hora local
    const localDate = date.includes('T') ? new Date(date) : new Date(date + 'T00:00:00');
    return localDate.toLocaleDateString("es-ES", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

/**
 * Retorna el nombre completo
 */
export function fullName(name, apellidos) {
    if (!name && !apellidos) return "";
    if (!name) return apellidos;
    if (!apellidos) return name;
    return `${name} ${apellidos}`;
}
