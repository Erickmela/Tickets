export const useToasts = (toastRef) => {
    const success = (titleOrMessage = 'Operación exitosa', message = '', position = 'top') => {
        // Si solo se pasa un argumento, usarlo como mensaje con título por defecto
        const title = message ? titleOrMessage : 'Operación exitosa';
        const msg = message ? message : titleOrMessage;
        toastRef.value?.addToast({ type: 'success', title, message: msg, position })
    }

    const error = (titleOrMessage = 'Error inesperado', message = '', position = 'top') => {
        const title = message ? titleOrMessage : 'Error inesperado';
        const msg = message ? message : titleOrMessage;
        toastRef.value?.addToast({ type: 'error', title, message: msg, position })
    }

    const info = (titleOrMessage = 'Atención', message = '', position = 'top') => {
        const title = message ? titleOrMessage : 'Atención';
        const msg = message ? message : titleOrMessage;
        toastRef.value?.addToast({ type: 'info', title, message: msg, position })
    }

    const warning = (titleOrMessage = 'Advertencia', message = '', position = 'top') => {
        const title = message ? titleOrMessage : 'Advertencia';
        const msg = message ? message : titleOrMessage;
        toastRef.value?.addToast({ type: 'warning', title, message: msg, position })
    }

    const validate = () => {
        info('Atención', 'Por favor corrige los errores en el formulario.', 'bottom')
    }

    return {
        success,
        error,
        info,
        warning,
        validate
    }
}
