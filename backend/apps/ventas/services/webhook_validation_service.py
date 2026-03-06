"""
Servicio de Validación de Webhooks de MercadoPago
Responsabilidad: Validar la autenticidad de las notificaciones de MP
"""
import hmac
import hashlib
import logging
from typing import Optional, Dict
from django.conf import settings

logger = logging.getLogger(__name__)


class WebhookValidationService:
    """
    Servicio para validar webhooks de MercadoPago usando HMAC-SHA256
    Implementa las especificaciones de seguridad de MP
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Inicializar servicio con la clave secreta
        
        Args:
            secret_key: Clave secreta de webhook de MP (si no se provee, se obtiene de settings)
        """
        self.secret_key = secret_key or getattr(settings, 'MERCADOPAGO_WEBHOOK_SECRET', None)
    
    def validate_signature(
        self,
        signature: Optional[str],
        data_id: Optional[str],
        x_request_id: Optional[str],
        is_production: bool = True
    ) -> bool:
        """
        Validar la firma del webhook de MercadoPago
        
        Args:
            signature: Header x-signature de la notificación
            data_id: Query param data_id
            x_request_id: Header x-request-id
            is_production: Si es ambiente de producción
            
        Returns:
            True si la firma es válida
        """
        # En desarrollo, omitir validación
        if not is_production:
            logger.info('Webhook: Validación de firma omitida (entorno de desarrollo)')
            return True
        
        # Validaciones básicas
        if not self._has_required_headers(signature):
            logger.warning('Webhook: Falta firma (x-signature) o Secret Key')
            return False
        
        if not self._has_required_params(data_id, x_request_id):
            logger.warning('Webhook: Faltan parámetros necesarios (data_id o x-request-id)')
            return False
        
        # Extraer componentes de la firma
        signature_components = self._extract_signature_components(signature)
        
        if not signature_components:
            logger.warning('Webhook: No se pudo extraer componentes de la firma')
            return False
        
        # Validar firma
        return self._verify_hmac_signature(
            data_id=data_id,
            x_request_id=x_request_id,
            ts=signature_components['ts'],
            received_hash=signature_components['hash']
        )
    
    def _has_required_headers(self, signature: Optional[str]) -> bool:
        """
        Verificar si tiene los headers requeridos
        
        Args:
            signature: Valor del header x-signature
            
        Returns:
            True si tiene los headers necesarios
        """
        return bool(signature and self.secret_key)
    
    def _has_required_params(self, data_id: Optional[str], x_request_id: Optional[str]) -> bool:
        """
        Verificar si tiene los parámetros requeridos
        
        Args:
            data_id: ID del pago
            x_request_id: ID de la request
            
        Returns:
            True si tiene los parámetros necesarios
        """
        return bool(data_id and x_request_id)
    
    def _extract_signature_components(self, signature: str) -> Optional[Dict[str, str]]:
        """
        Extraer timestamp y hash de la firma
        
        Args:
            signature: Firma del webhook en formato 'ts=xxx,v1=yyy'
            
        Returns:
            Dict con 'ts' y 'hash' o None si hay error
        """
        parts = signature.split(',')
        ts = None
        hash_value = None
        
        for part in parts:
            key_value = part.split('=', 1)
            
            if len(key_value) != 2:
                continue
            
            key = key_value[0].strip()
            value = key_value[1].strip()
            
            if key == 'ts':
                ts = value
            elif key == 'v1':
                hash_value = value
        
        if not ts or not hash_value:
            return None
        
        return {
            'ts': ts,
            'hash': hash_value,
        }
    
    def _verify_hmac_signature(
        self,
        data_id: str,
        x_request_id: str,
        ts: str,
        received_hash: str
    ) -> bool:
        """
        Verificar firma HMAC-SHA256
        
        Args:
            data_id: ID del pago
            x_request_id: ID de la request
            ts: Timestamp de la firma
            received_hash: Hash recibido en la firma
            
        Returns:
            True si la firma es válida
        """
        # Construir manifiesto según formato oficial de MercadoPago
        # Formato: id:[data_id];request-id:[x-request-id];ts:[ts];
        manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
        
        # Calcular hash HMAC-SHA256
        calculated_hash = hmac.new(
            key=self.secret_key.encode('utf-8'),
            msg=manifest.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Comparación segura contra timing attacks
        is_valid = hmac.compare_digest(calculated_hash, received_hash)
        
        if not is_valid:
            logger.error('Webhook: Error de validación de firma', extra={
                'manifest': manifest,
                'expected': received_hash,
                'calculated': calculated_hash,
            })
        
        return is_valid
    
    @staticmethod
    def is_payment_notification(notification_type: Optional[str]) -> bool:
        """
        Validar que la notificación sea de tipo payment
        
        Args:
            notification_type: Tipo de notificación (topic o type)
            
        Returns:
            True si es notificación de pago
        """
        return notification_type == 'payment'
    
    @staticmethod
    def is_webhook(has_action: bool) -> bool:
        """
        Verificar si es un webhook (vs IPN)
        
        Args:
            has_action: Si la request tiene el campo 'action'
            
        Returns:
            True si es webhook
        """
        return has_action
