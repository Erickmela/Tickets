"""
Servicio de generación de códigos QR
Responsabilidad: Crear códigos QR seguros con encriptación
"""
import qrcode
from io import BytesIO
from django.core.files import File
from config.encryption import ticket_encryption


class QRCodeService:
    """
    Servicio para generación de códigos QR con encriptación avanzada
    Responsabilidad única: Crear y guardar QR codes seguros
    """
    
    @staticmethod
    def generar_qr(
        codigo_uuid: str, 
        ticket_id: int = None, 
        usar_encriptacion: bool = True, 
        validity_hours: int = 8760
    ) -> tuple:
        """
        Genera un código QR con encriptación opcional y validez configurable
        
        Args:
            codigo_uuid: UUID del ticket
            ticket_id: ID del ticket
            usar_encriptacion: Si True, usa AES-256 + HMAC (MÁS SEGURO)
            validity_hours: Horas de validez del token (default: 1 año)
        """
        if usar_encriptacion:
            # MODO SEGURO: Encriptar UUID con AES-256 + HMAC
            token_encriptado = ticket_encryption.encrypt_ticket_data(
                ticket_uuid=codigo_uuid,
                ticket_id=ticket_id,
                validity_hours=validity_hours
            )
            qr_data = token_encriptado
        else:
            # MODO BÁSICO: UUID en texto plano (menos seguro)
            token_encriptado = None
            qr_data = str(codigo_uuid)
        
        # Generar QR con alto nivel de corrección de errores
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% de corrección
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return File(buffer, name=f'{codigo_uuid}.png'), token_encriptado
