"""
Servicios de negocio para Ventas y Tickets
Aplicando Single Responsibility - Lógica de negocio separada
"""
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from django.core.files import File
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Venta, Ticket
from apps.usuarios.models import PerfilCliente, Usuario, RolUsuario
from config.encryption import ticket_encryption


class QRCodeService:
    """
    Servicio para generación de códigos QR con encriptación avanzada
    Responsabilidad única: Crear y guardar QR codes seguros
    """
    
    @staticmethod
    def generar_qr(codigo_uuid: str, ticket_id: int = None, usar_encriptacion: bool = True, validity_hours: int = 8760) -> tuple:
        """
        Genera un código QR con encriptación opcional y validez configurable
        
        Args:
            codigo_uuid: UUID del ticket
            ticket_id: ID del ticket
            usar_encriptacion: Si True, usa AES-256 + HMAC (MÁS SEGURO)
            validity_hours: Horas de validez del token (default: 1 año)
        
        Returns:
            Tuple (File del QR, token_encriptado or None)
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


class VentaService:
    """
    Servicio para gestión de ventas
    Responsabilidad: Coordinar la creación de ventas con validaciones de negocio
    """
    
    @staticmethod
    @transaction.atomic
    def crear_venta(vendedor, datos_venta: dict, tickets_data: list) -> Venta:
        """
        Crea una venta completa con todos sus tickets
        Aplica transaccionalidad: si algo falla, se hace rollback completo
        
        ARQUITECTURA UNIFICADA:
        - Al crear un cliente, se crea Usuario (rol=CLIENTE) + PerfilCliente vinculado
        - Todos los usuarios tienen Usuario + PerfilCliente
        - La diferencia está en el rol: CLIENTE vs ADMIN/VENDEDOR/VALIDADOR

        Returns:
            Venta creada con todos sus tickets
        """
        # Paso 1: Obtener o crear el cliente (Usuario + PerfilCliente)
        cliente_dni = datos_venta['cliente_dni']
        cliente_nombre = datos_venta['cliente_nombre']
        cliente_telefono = datos_venta.get('cliente_telefono', '')
        cliente_email = datos_venta.get('cliente_email', '')
        
        try:
            # Buscar si ya existe el perfil
            cliente = PerfilCliente.objects.get(dni=cliente_dni)
            
            # Actualizar datos si cambiaron
            actualizado = False
            if cliente.nombre_completo != cliente_nombre:
                cliente.nombre_completo = cliente_nombre
                actualizado = True
            if cliente_telefono and cliente.telefono != cliente_telefono:
                cliente.telefono = cliente_telefono
                actualizado = True
            
            if actualizado:
                cliente.save()
            
            # Actualizar email en Usuario si cambió
            if cliente.usuario and cliente_email and cliente.usuario.email != cliente_email:
                cliente.usuario.email = cliente_email
                cliente.usuario.save()
            
            # Si no tiene Usuario vinculado, crear uno
            if not cliente.usuario:
                username = f"cliente_{cliente_dni}"
                usuario = Usuario.objects.create_user(
                    username=username,
                    email=cliente_email if cliente_email else f"{cliente_dni}@temp.com",
                    password=cliente_dni,  # Password temporal = DNI
                    rol=RolUsuario.CLIENTE
                )
                usuario.is_staff = False
                usuario.save()
                
                cliente.usuario = usuario
                cliente.save()
        
        except PerfilCliente.DoesNotExist:
            # Crear nuevo Usuario + PerfilCliente
            username = f"cliente_{cliente_dni}"
            
            # Crear Usuario con rol CLIENTE
            usuario = Usuario.objects.create_user(
                username=username,
                email=cliente_email if cliente_email else f"{cliente_dni}@temp.com",
                password=cliente_dni,  # Password temporal = DNI
                rol=RolUsuario.CLIENTE
            )
            usuario.is_staff = False  # Los clientes no son staff
            usuario.save()
            
            # Crear PerfilCliente vinculado
            cliente = PerfilCliente.objects.create(
                usuario=usuario,
                dni=cliente_dni,
                nombre_completo=cliente_nombre,
                telefono=cliente_telefono
            )
        
        # Paso 2: Calcular el total
        from apps.eventos.models import Zona
        total = 0
        for ticket_data in tickets_data:
            zona = Zona.objects.get(id=ticket_data['zona_id'])
            total += zona.precio
        
        # Paso 3: Crear la venta
        venta = Venta.objects.create(
            vendedor=vendedor,
            cliente_pagador=cliente,
            total_pagado=total,
            metodo_pago=datos_venta['metodo_pago'],
            nro_operacion=datos_venta.get('nro_operacion', ''),
            observaciones=datos_venta.get('observaciones', '')
        )
        
        # Paso 4: Crear los tickets
        tickets_creados = []
        for ticket_data in tickets_data:
            try:
                ticket = Ticket.objects.create(
                    venta=venta,
                    zona_id=ticket_data['zona_id'],
                    dni_titular=ticket_data['dni_titular'],
                    nombre_titular=ticket_data['nombre_titular']
                )
                
                # Calcular validez dinámica del token basada en la fecha del evento
                zona = Zona.objects.get(id=ticket_data['zona_id'])
                evento = zona.evento
                
                if evento.fecha_evento:
                    # Token válido hasta 7 días después del evento
                    dias_hasta_evento = (evento.fecha_evento - datetime.now().date()).days
                    validity_hours = max((dias_hasta_evento + 7) * 24, 24)  # Mínimo 24 horas
                else:
                    # Fallback: 1 año si no hay fecha configurada
                    validity_hours = 8760
                
                # Generar QR code con ENCRIPTACIÓN AVANZADA (AES-256 + HMAC)
                qr_file, token_encriptado = QRCodeService.generar_qr(
                    codigo_uuid=ticket.codigo_uuid,
                    ticket_id=ticket.id,
                    usar_encriptacion=True,  # Activar encriptación para máxima seguridad
                    validity_hours=validity_hours  # Validez dinámica basada en fecha del evento
                )
                
                # Guardar QR y token encriptado
                ticket.qr_image.save(f'{ticket.codigo_uuid}.png', qr_file, save=False)
                ticket.token_encriptado = token_encriptado
                ticket.save()
                
                tickets_creados.append(ticket)
            except ValidationError as e:
                # Si un ticket falla, la transacción completa se revierte
                raise ValidationError(f'Error al crear ticket: {str(e)}')
        
        return venta
