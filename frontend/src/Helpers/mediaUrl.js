// src/Helpers/mediaUrl.js
// Centraliza la generación de URLs para recursos multimedia

const BASE_MEDIA_URL = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8000/media';

/**
 * Genera la URL completa para un recurso en /media/
 * @param {string} path - Ruta relativa del recurso (ej: 'eventos/banners/imagen.jpg')
 * @returns {string} URL absoluta del recurso
 */
export function getMediaUrl(path) {
  if (!path) return '';
  // Evita doble barra si path ya empieza con /
  return `${BASE_MEDIA_URL}/${path.replace(/^\/+/, '')}`;
}

export default getMediaUrl;
