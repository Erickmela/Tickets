"""
Utilidad para encriptar y desencriptar IDs
Para proteger los IDs numéricos en las URLs
"""
from hashids import Hashids
from django.conf import settings

# Obtener la clave secreta del settings
SECRET_SALT = getattr(settings, 'SECRET_KEY', 'jala-jala-tickets-secret-key-2024')

# Crear instancia de Hashids con configuración personalizada
hashids = Hashids(
    salt=SECRET_SALT,
    min_length=8,  # Longitud mínima del hash
    alphabet='abcdefghijklmnopqrstuvwxyz0123456789'  # Solo minúsculas y números
)


def encode_id(id_value):
    """
    Encripta un ID numérico a un string ofuscado
    
    Args:
        id_value: ID numérico a encriptar
    
    Returns:
        String encriptado
    """
    if not id_value:
        return None
    try:
        return hashids.encode(int(id_value))
    except (ValueError, TypeError):
        return None


def decode_id(encoded_value):
    """
    Desencripta un string ofuscado a un ID numérico
    
    Args:
        encoded_value: String encriptado
    
    Returns:
        ID numérico original o None si no es válido
    """
    if not encoded_value:
        return None
    try:
        decoded = hashids.decode(encoded_value)
        return decoded[0] if decoded else None
    except (ValueError, TypeError, IndexError):
        return None


def encode_multiple_ids(*ids):
    """
    Encripta múltiples IDs en un solo string
    
    Args:
        *ids: Múltiples IDs numéricos
    
    Returns:
        String encriptado con múltiples IDs
    """
    try:
        int_ids = [int(id_val) for id_val in ids if id_val]
        return hashids.encode(*int_ids)
    except (ValueError, TypeError):
        return None


def decode_multiple_ids(encoded_value):
    """
    Desencripta un string a múltiples IDs numéricos
    
    Args:
        encoded_value: String encriptado
    
    Returns:
        Tupla con los IDs numéricos originales
    """
    if not encoded_value:
        return None
    try:
        return hashids.decode(encoded_value)
    except (ValueError, TypeError):
        return None
