/**
 * Funciones de utilidad para extraer IDs de videos de diferentes plataformas
 * Soporta: YouTube, Vimeo, Bunny.net
 */

/**
 * Extrae el src de un iframe HTML
 * @param {string} input - Código HTML del iframe
 * @returns {string} URL del src o input original si no es iframe
 */
const extractSrcFromIframe = (input) => {
    if (!input || !input.includes('<iframe')) return input;

    const srcMatch = input.match(/src=["']([^"']+)["']/);
    return srcMatch ? srcMatch[1] : input;
};

/**
 * Extrae el ID de un video de YouTube
 * @param {string} input - URL, iframe o ID de YouTube
 * @returns {string} ID del video o string vacío si no se encuentra
 *
 * @example
 * extractYoutubeId('https://www.youtube.com/watch?v=dQw4w9WgXcQ') // 'dQw4w9WgXcQ'
 * extractYoutubeId('https://youtu.be/dQw4w9WgXcQ') // 'dQw4w9WgXcQ'
 * extractYoutubeId('<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>') // 'dQw4w9WgXcQ'
 */
export const extractYoutubeId = (input) => {
    if (!input) return '';

    try {
        const url = extractSrcFromIframe(input);

        // Extraer ID de diferentes formatos
        // youtube.com/watch?v=VIDEO_ID
        // youtu.be/VIDEO_ID
        // youtube.com/embed/VIDEO_ID
        const patterns = [
            /(?:youtube\.com\/watch\?v=)([^&?\/]+)/,
            /(?:youtu\.be\/)([^&?\/]+)/,
            /(?:youtube\.com\/embed\/)([^&?\/]+)/
        ];

        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) return match[1];
        }

        return '';
    } catch (error) {
        console.error('Error extrayendo ID de YouTube:', error);
        return '';
    }
};

/**
 * Extrae el ID de un video de Vimeo
 * @param {string} input - URL, iframe o ID de Vimeo
 * @returns {string} ID del video o string vacío si no se encuentra
 *
 * @example
 * extractVimeoId('https://vimeo.com/123456789') // '123456789'
 * extractVimeoId('https://player.vimeo.com/video/123456789') // '123456789'
 * extractVimeoId('<iframe src="https://player.vimeo.com/video/123456789"></iframe>') // '123456789'
 */
export const extractVimeoId = (input) => {
    if (!input) return '';

    try {
        const url = extractSrcFromIframe(input);

        // vimeo.com/VIDEO_ID
        // player.vimeo.com/video/VIDEO_ID
        const patterns = [
            /(?:vimeo\.com\/)(\d+)/,
            /(?:player\.vimeo\.com\/video\/)(\d+)/
        ];

        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) return match[1];
        }

        return '';
    } catch (error) {
        console.error('Error extrayendo ID de Vimeo:', error);
        return '';
    }
};

/**
 * Extrae el ID de un video de Bunny.net (formato: BIBLIOTECA_ID/VIDEO_ID)
 * @param {string} input - URL, iframe o ID de Bunny.net
 * @returns {string} ID en formato "biblioteca_id/video_id" o string vacío si no se encuentra
 *
 * @example
 * extractBunnynetId('https://iframe.mediadelivery.net/embed/123456/abc-def-ghi') // '123456/abc-def-ghi'
 * extractBunnynetId('https://iframe.mediadelivery.net/play/123456/abc-def-ghi') // '123456/abc-def-ghi'
 * extractBunnynetId('<iframe src="https://iframe.mediadelivery.net/embed/123456/abc-def-ghi"></iframe>') // '123456/abc-def-ghi'
 */
export const extractBunnynetId = (input) => {
    if (!input) return '';

    try {
        const url = extractSrcFromIframe(input);

        // iframe.mediadelivery.net/embed/BIBLIOTECA_ID/VIDEO_ID
        // iframe.mediadelivery.net/play/BIBLIOTECA_ID/VIDEO_ID
        const pattern = /iframe\.mediadelivery\.net\/(?:embed|play)\/(\d+)\/([a-zA-Z0-9-]+)/;
        const match = url.match(pattern);

        if (match && match[1] && match[2]) {
            const bibliotecaId = match[1];
            const videoId = match[2];
            return `${bibliotecaId}/${videoId}`;
        }

        return '';
    } catch (error) {
        console.error('Error extrayendo ID de Bunny.net:', error);
        return '';
    }
};

/**
 * Detecta la plataforma de video basándose en el contenido
 * @param {string} input - URL, iframe o ID de video
 * @returns {string|null} Nombre de la plataforma: 'youtube', 'vimeo', 'bunny' o null
 *
 * @example
 * detectVideoPlatform('https://www.youtube.com/watch?v=abc123') // 'youtube'
 * detectVideoPlatform('https://vimeo.com/123456') // 'vimeo'
 * detectVideoPlatform('https://iframe.mediadelivery.net/embed/123/abc') // 'bunny'
 */
export const detectVideoPlatform = (input) => {
    if (!input) return null;

    const content = input.toLowerCase();

    if (content.includes('youtube.com') || content.includes('youtu.be')) {
        return 'youtube';
    }

    if (content.includes('vimeo.com')) {
        return 'vimeo';
    }

    if (content.includes('bunny.net') || content.includes('mediadelivery.net')) {
        return 'bunny';
    }

    return null;
};

/**
 * Extrae el ID de video según la plataforma detectada automáticamente
 * @param {string} input - URL, iframe o ID de video
 * @returns {object} Objeto con la plataforma y el ID extraído
 *
 * @example
 * extractVideoId('https://www.youtube.com/watch?v=abc123')
 * // { platform: 'youtube', id: 'abc123' }
 */
export const extractVideoId = (input) => {
    if (!input) return { platform: null, id: '' };

    const platform = detectVideoPlatform(input);

    switch (platform) {
        case 'youtube':
            return { platform: 'youtube', id: extractYoutubeId(input) };
        case 'vimeo':
            return { platform: 'vimeo', id: extractVimeoId(input) };
        case 'bunny':
            return { platform: 'bunny', id: extractBunnynetId(input) };
        default:
            return { platform: null, id: '' };
    }
};
