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

export function formatPrecio(precio) {
    if (!precio || precio === "0.00") return "Gratis";
    return `S/ ${parseFloat(precio).toFixed(2)}`;
};

export function formatUserName(user) {
    if (!user) return "";
    const name = user.name;
    const apellidos = user.apellidos;

    const primerNombre = name ? name.split(" ")[0] : "";
    const primerApellido = apellidos ? apellidos.split(" ")[0] : "";

    return primerApellido ? `${primerNombre} ${primerApellido}` : primerNombre;
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

export function formatDateShort(t) {
    if (!t) return "";
    let dateStr = String(t);
    if (!dateStr.includes('T')) {
        dateStr = dateStr.replace(/-/g, '/');
    }
    const date = new Date(dateStr);

    return new Intl.DateTimeFormat('es-PE', {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    }).format(date);
}

export function timeText(t) {
    const [h, m] = t.split(':').map(Number);
    const horas = h > 0 ? `${h} ${h === 1 ? 'hora' : 'horas'}` : '';
    const minutos = m > 0 ? `${m} ${m === 1 ? 'minuto' : 'minutos'}` : '';

    if (horas && minutos) return `${horas} y ${minutos}`;
    if (horas) return horas;
    if (minutos) return minutos;

    return '0 minutos';
}

export function hourText(t) {
    const [h, m] = t.split(':').map(Number);
    const horas = h > 0 ? `${h} ${h === 1 ? 'hora' : 'horas'}` : '';
    const minutos = m > 0 ? `${m} ${m === 1 ? 'minuto' : 'minutos'}` : '';

    if (horas && minutos) return `${horas}`;
    if (horas) return horas;
    if (minutos) return minutos;

    return '0 minutos';
}


export function timeTextSmall(t) {
    const [h, m] = t.split(':').map(Number);
    const horas = h > 0 ? `${h} ${h === 1 ? 'h' : 'h'}` : '';
    const minutos = m > 0 ? `${m} ${m === 1 ? 'min' : 'min'}` : '';

    if (horas && minutos) return `${horas} y ${minutos}`;
    if (horas) return horas;
    if (minutos) return minutos;

    return '0 min';
}

export function timeSmall(t) {
    if (!t) return "0:00";
    const [h, m, s] = t.split(':').map(Number);
    return h > 0 ? `${h}:${m}:${s}` : `${m}:${s}`;
}

export const getNivelText = (nivel) => {
    switch (Number(nivel)) {
        case 1:
            return "Básico";
        case 2:
            return "Intermedio";
        case 3:
            return "Avanzado";
        default:
            return "";
    }
};

export function getNivelClass(nivel) {
    switch (Number(nivel)) {
        case 1:
            return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
        case 2:
            return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
        case 3:
            return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
        default:
            return "";
    }
};

export function dateText(date) {
    if (!date) return "";
    // Agregar 'T00:00:00' para forzar interpretación como hora local
    const localDate = date.includes('T') ? new Date(date) : new Date(date + 'T00:00:00');
    return localDate.toLocaleDateString("es-ES", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
};

export function dateTextSmall(date) {
    if (!date) return "";
    // Agregar 'T00:00:00' para forzar interpretación como hora local
    const localDate = date.includes('T') ? new Date(date) : new Date(date + 'T00:00:00');
    return localDate.toLocaleDateString("es-ES", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
};

export function monthYearText(date) {
    if (!date) return "";
    // Agregar 'T00:00:00' para forzar interpretación como hora local
    const localDate = date.includes('T') ? new Date(date) : new Date(date + 'T00:00:00');
    const text = localDate.toLocaleDateString("es-ES", {
        year: "numeric",
        month: "short"
    });
    return text.charAt(0).toUpperCase() + text.slice(1);
};

export function fullName(name, apellidos) {
    if (!name && !apellidos) return "";
    if (!name) return apellidos;
    if (!apellidos) return name;
    return `${name} ${apellidos}`;
}

export function hasRole(role, container) {
    const roles = Array.isArray(role) ? role : [role];
    if (Array.isArray(container)) {
        return roles.some(r => container.includes(r));
    } else if (typeof container === 'object' && container !== null) {
        return roles.some(r => !!container[r]);
    }
    return false;
}

export function clearPhone(phone) {
    return phone.replace(/\s/g, '');
}

export function generatePassword(length = 8) {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let password = "";
    for (let i = 0; i < length; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
}
