"""
Servicio de Encriptación para Tickets - Seguridad Avanzada
Implementa AES-256-CBC + HMAC-SHA256 para máxima seguridad

ARQUITECTURA DE SEGURIDAD:
1. AES-256-CBC: Encriptación de datos (estándar militar)
2. HMAC-SHA256: Verificación de integridad (anti-manipulación)
3. IV aleatorio: Previene patrones repetidos
4. Timestamp: Detecta tickets expirados o clonados

FORMATO DEL TOKEN ENCRIPTADO:
[IV:16 bytes][Datos Encriptados:N bytes][HMAC:32 bytes]
Todo en Base64URL para uso en QR codes
"""
import os
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.conf import settings


class TicketEncryptionService:
    """
    Responsabilidad: Proteger códigos de tickets con múltiples capas de seguridad
    """
    
    # Tamaños definidos para AES-256
    KEY_SIZE = 32  # 256 bits
    IV_SIZE = 16   # 128 bits (bloque AES)
    HMAC_SIZE = 32 # 256 bits (SHA-256)
    
    def __init__(self):
        """Inicializar con claves del sistema"""
        self.encryption_key = self._get_encryption_key()
        self.hmac_key = self._get_hmac_key()
    
    def _get_encryption_key(self) -> bytes:
        """Obtener clave de encriptación desde configuración"""
        key = getattr(settings, 'TICKET_ENCRYPTION_KEY', None)
        if not key:
            raise ValueError(
                "TICKET_ENCRYPTION_KEY no está configurada en settings. "
                "Genera una clave segura con: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        return bytes.fromhex(key)
    
    def _get_hmac_key(self) -> bytes:
        """Obtener clave HMAC desde configuración"""
        key = getattr(settings, 'TICKET_HMAC_KEY', None)
        if not key:
            raise ValueError(
                "TICKET_HMAC_KEY no está configurada en settings. "
                "Genera una clave segura con: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        return bytes.fromhex(key)
    
    def encrypt_ticket_data(self, ticket_uuid: str, ticket_id: int = None, 
                           validity_hours: int = 720) -> str:
        """
        Encripta datos del ticket con AES-256 + HMAC
        
        Args:
            ticket_uuid: UUID del ticket
            ticket_id: ID opcional del ticket
            validity_hours: Horas de validez (default: 30 días)
        
        Returns:
            Token encriptado en Base64URL
        """
        # Preparar datos a encriptar
        issue_time = datetime.utcnow()
        expiry_time = issue_time + timedelta(hours=validity_hours)
        
        payload = {
            'uuid': str(ticket_uuid),
            'id': ticket_id,
            'issued_at': issue_time.isoformat(),
            'expires_at': expiry_time.isoformat(),
            'version': '2',  # Versión del formato de encriptación
        }
        
        # Convertir a JSON
        plaintext = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        
        # Añadir padding PKCS7
        plaintext = self._add_padding(plaintext)
        
        # Generar IV aleatorio único para cada ticket
        iv = os.urandom(self.IV_SIZE)
        
        # Encriptar con AES-256-CBC
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # Concatenar IV + Ciphertext
        encrypted_data = iv + ciphertext
        
        # Calcular HMAC para verificar integridad
        hmac_digest = hmac.new(
            self.hmac_key,
            encrypted_data,
            hashlib.sha256
        ).digest()
        
        # Formato final: [IV][Ciphertext][HMAC]
        final_token = encrypted_data + hmac_digest
        
        # Codificar en Base64URL (seguro para URLs y QR)
        return base64.urlsafe_b64encode(final_token).decode('ascii').rstrip('=')
    
    def decrypt_ticket_data(self, encrypted_token: str) -> dict:
        """
        Desencripta y valida el token del ticket
        
        Args:
            encrypted_token: Token encriptado en Base64URL
        
        Returns:
            Dict con los datos del ticket
        
        Raises:
            ValueError: Si el token es inválido o ha sido manipulado
        """
        try:
            # Añadir padding si fue removido
            padding = 4 - (len(encrypted_token) % 4)
            if padding != 4:
                encrypted_token += '=' * padding
            
            # Decodificar Base64URL
            token_bytes = base64.urlsafe_b64decode(encrypted_token.encode('ascii'))
            
            # Verificar tamaño mínimo
            min_size = self.IV_SIZE + 16 + self.HMAC_SIZE  # IV + 1 bloque mínimo + HMAC
            if len(token_bytes) < min_size:
                raise ValueError("Token demasiado corto")
            
            # Separar componentes
            encrypted_data = token_bytes[:-self.HMAC_SIZE]
            received_hmac = token_bytes[-self.HMAC_SIZE:]
            
            # VERIFICACIÓN DE INTEGRIDAD: Validar HMAC
            calculated_hmac = hmac.new(
                self.hmac_key,
                encrypted_data,
                hashlib.sha256
            ).digest()
            
            if not hmac.compare_digest(calculated_hmac, received_hmac):
                raise ValueError("Token manipulado: HMAC inválido")
            
            # Separar IV y ciphertext
            iv = encrypted_data[:self.IV_SIZE]
            ciphertext = encrypted_data[self.IV_SIZE:]
            
            # Desencriptar con AES-256-CBC
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remover padding PKCS7
            plaintext = self._remove_padding(plaintext_padded)
            
            # Parsear JSON
            payload = json.loads(plaintext.decode('utf-8'))
            
            # Validar expiración
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.utcnow() > expires_at:
                raise ValueError(f"Token expirado (venció el {expires_at.isoformat()})")
            
            return payload
        
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Token inválido: {str(e)}")
    
    def _add_padding(self, data: bytes) -> bytes:
        """Añadir padding PKCS7 a los datos"""
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _remove_padding(self, data: bytes) -> bytes:
        """Remover padding PKCS7 de los datos"""
        padding_length = data[-1]
        
        # Validar padding
        if padding_length < 1 or padding_length > 16:
            raise ValueError("Padding inválido")
        
        for i in range(padding_length):
            if data[-(i+1)] != padding_length:
                raise ValueError("Padding corrupto")
        
        return data[:-padding_length]
    
    def verify_ticket_token(self, encrypted_token: str, expected_uuid: str = None) -> bool:
        """
        Verifica si un token es válido y corresponde al UUID esperado
        
        Args:
            encrypted_token: Token a verificar
            expected_uuid: UUID esperado (opcional)
        
        Returns:
            True si es válido, False en caso contrario
        """
        try:
            payload = self.decrypt_ticket_data(encrypted_token)
            
            # Si se proporciona UUID esperado, verificarlo
            if expected_uuid and payload['uuid'] != str(expected_uuid):
                return False
            
            return True
        
        except (ValueError, KeyError):
            return False


# Instancia global del servicio
ticket_encryption = TicketEncryptionService()
