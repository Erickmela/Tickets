"""
Servicio de Mapeo de Estados de Pago de MercadoPago
Responsabilidad: Convertir estados de MP a estados locales del sistema
"""
from typing import Optional, Dict


class PaymentStatusMapper:
    """
    Mapea estados de MercadoPago a estados de orden locales
    Basado en la documentación oficial de MP
    """
    
    # Estados de MercadoPago
    MP_APPROVED = 'approved'
    MP_PENDING = 'pending'
    MP_IN_PROCESS = 'in_process'
    MP_REJECTED = 'rejected'
    MP_CANCELLED = 'cancelled'
    MP_REFUNDED = 'refunded'
    MP_CHARGED_BACK = 'charged_back'
    MP_EXPIRED = 'expired'
    
    # Estados de orden locales
    ORDER_COMPLETED = 'completado'
    ORDER_PENDING = 'pendiente'
    ORDER_CANCELLED = 'cancelado'
    ORDER_REFUNDED = 'reembolsado'
    ORDER_EXPIRED = 'expirado'
    
    # Mapeo principal por status
    STATUS_MAP = {
        MP_APPROVED: ORDER_COMPLETED,
        MP_PENDING: ORDER_PENDING,
        MP_IN_PROCESS: ORDER_PENDING,
        MP_REFUNDED: ORDER_REFUNDED,
        MP_CHARGED_BACK: ORDER_REFUNDED,
        MP_EXPIRED: ORDER_EXPIRED,
        MP_REJECTED: ORDER_CANCELLED,
        MP_CANCELLED: ORDER_CANCELLED,
    }
    
    @classmethod
    def map_to_order_status(cls, mp_status: Optional[str], mp_status_detail: Optional[str] = None) -> str:
        """
        Mapear estado de MercadoPago a estado de orden local
        
        Args:
            mp_status: Estado principal del pago en MP
            mp_status_detail: Detalle del estado para casos específicos
            
        Returns:
            Estado de orden local
        """
        if not mp_status:
            return cls.ORDER_CANCELLED
        
        # Mapeo directo por status
        if mp_status in cls.STATUS_MAP:
            return cls.STATUS_MAP[mp_status]
        
        # Verificar status_detail para casos específicos
        if mp_status_detail:
            detail_status = cls._map_by_status_detail(mp_status_detail)
            if detail_status:
                return detail_status
        
        # Por defecto, cancelado
        return cls.ORDER_CANCELLED
    
    @classmethod
    def _map_by_status_detail(cls, status_detail: str) -> Optional[str]:
        """
        Mapear por status_detail cuando sea necesario
        
        Args:
            status_detail: Detalle del estado de MP
            
        Returns:
            Estado local o None si no aplica
        """
        lower = status_detail.lower()
        
        # Keywords que indican cancelación o rechazo
        cancel_keywords = ['rejected', 'cancelled', 'expired', 'invalid']
        
        for keyword in cancel_keywords:
            if keyword in lower:
                return cls.ORDER_CANCELLED
        
        return None
    
    @classmethod
    def is_final_status(cls, mp_status: str) -> bool:
        """
        Verificar si el estado es final (no cambiará)
        
        Args:
            mp_status: Estado de MP
            
        Returns:
            True si el estado es final
        """
        final_statuses = [
            cls.MP_APPROVED,
            cls.MP_REJECTED,
            cls.MP_CANCELLED,
            cls.MP_REFUNDED,
            cls.MP_CHARGED_BACK,
            cls.MP_EXPIRED,
        ]
        return mp_status in final_statuses
    
    @classmethod
    def requires_user_action(cls, mp_status: str) -> bool:
        """
        Verificar si el estado requiere acción del usuario
        
        Args:
            mp_status: Estado de MP
            
        Returns:
            True si requiere acción del usuario
        """
        return mp_status in [cls.MP_PENDING, cls.MP_IN_PROCESS]
    
    @classmethod
    def is_successful(cls, mp_status: str) -> bool:
        """
        Verificar si el pago fue exitoso
        
        Args:
            mp_status: Estado de MP
            
        Returns:
            True si el pago fue aprobado
        """
        return mp_status == cls.MP_APPROVED
    
    @classmethod
    def is_rejected(cls, mp_status: str) -> bool:
        """
        Verificar si el pago fue rechazado
        
        Args:
            mp_status: Estado de MP
            
        Returns:
            True si el pago fue rechazado
        """
        rejected_statuses = [
            cls.MP_REJECTED,
            cls.MP_CANCELLED,
            cls.MP_EXPIRED,
        ]
        return mp_status in rejected_statuses
    
    @classmethod
    def get_user_friendly_message(cls, mp_status: str, status_detail: Optional[str] = None) -> str:
        """
        Obtener mensaje amigable para el usuario
        
        Args:
            mp_status: Estado de MP
            status_detail: Detalle del estado
            
        Returns:
            Mensaje descriptivo para el usuario
        """
        messages = {
            cls.MP_APPROVED: 'Tu pago ha sido aprobado exitosamente.',
            cls.MP_PENDING: 'Tu pago está pendiente de confirmación.',
            cls.MP_IN_PROCESS: 'Tu pago está siendo procesado.',
            cls.MP_REJECTED: 'Tu pago fue rechazado. Por favor, intenta con otro método de pago.',
            cls.MP_CANCELLED: 'El pago fue cancelado.',
            cls.MP_EXPIRED: 'El pago ha expirado. Por favor, intenta nuevamente.',
            cls.MP_REFUNDED: 'El pago ha sido reembolsado.',
            cls.MP_CHARGED_BACK: 'Se ha procesado un contracargo.',
        }
        
        message = messages.get(mp_status, 'Estado de pago desconocido.')
        
        # Agregar detalles adicionales si existen
        if status_detail:
            detail_message = cls._get_status_detail_message(status_detail)
            if detail_message:
                message += ' ' + detail_message
        
        return message
    
    @classmethod
    def _get_status_detail_message(cls, status_detail: str) -> str:
        """
        Obtener mensaje específico del status_detail
        
        Args:
            status_detail: Detalle del estado de MP
            
        Returns:
            Mensaje descriptivo o cadena vacía
        """
        detail_messages = {
            'cc_rejected_insufficient_amount': 'Fondos insuficientes.',
            'cc_rejected_bad_filled_security_code': 'Código de seguridad inválido.',
            'cc_rejected_bad_filled_date': 'Fecha de vencimiento inválida.',
            'cc_rejected_bad_filled_other': 'Revisa los datos de tu tarjeta.',
            'cc_rejected_call_for_authorize': 'Debes autorizar el pago con tu entidad bancaria.',
            'cc_rejected_card_disabled': 'Tu tarjeta está deshabilitada.',
            'cc_rejected_duplicated_payment': 'Ya existe un pago con estos datos.',
            'cc_rejected_high_risk': 'El pago fue rechazado por seguridad.',
            'pending_waiting_payment': 'Esperando confirmación del pago.',
        }
        
        return detail_messages.get(status_detail, '')
