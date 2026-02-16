import axios from 'axios';
import { router } from '@inertiajs/vue3';

export function esAutenticate(user) {
    if (!user) {
        axios.post(route('set.intended'), {
            intended_url: window.location.pathname
        }).then(() => {
            router.visit(route('login'));
        });
        return false;
    }
    return true;
}
