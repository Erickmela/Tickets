import { ref } from 'vue'

export default function Dropdown() {
  const showDropdown = ref(false)
  const selectItem = ref(null)
  const menuX = ref(0)
  const menuY = ref(0)

  /**
   * Abre el menú contextual y guarda el item y posición del evento
   */
  const abrirMenu = (item, event) => {
    event.preventDefault();
    event.stopPropagation();
    
    selectItem.value = item
    menuX.value = event.clientX
    menuY.value = event.clientY
    showDropdown.value = true
    
    // Cerrar el menú al hacer click fuera
    setTimeout(() => {
      document.addEventListener('click', cerrarMenu);
    }, 100);
  }

  /**
   * Cierra el menú contextual
   */
  const cerrarMenu = () => {
    showDropdown.value = false
    selectItem.value = null
    document.removeEventListener('click', cerrarMenu);
  }

  return {
    showDropdown,
    selectItem,
    menuX,
    menuY,
    abrirMenu,
    cerrarMenu,
  }
}
