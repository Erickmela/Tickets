"""
Servicio de gestión de ventas
Responsabilidad: Lógica de negocio para creación de ventas
"""
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.ventas.models import Venta, Ticket
from apps.usuarios.models import PerfilCliente, Usuario, RolUsuario
from apps.eventos.models import Zona
from .qr_service import QRCodeService


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
        """
        # Paso 1: Obtener o crear el cliente (Usuario + PerfilCliente)
        cliente = VentaService._obtener_o_crear_cliente(datos_venta)
        
        # Paso 2: Calcular el total de la venta
        total = VentaService._calcular_total(tickets_data)
        
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
        VentaService._crear_tickets(venta, tickets_data)
        
        return venta
    
    @staticmethod
    def _obtener_o_crear_cliente(datos_venta: dict) -> PerfilCliente:
        """Obtener o crear un cliente con su usuario asociado"""
        cliente_dni = datos_venta['cliente_dni']
        cliente_nombre = datos_venta['cliente_nombre']
        cliente_telefono = datos_venta.get('cliente_telefono', '')
        cliente_email = datos_venta.get('cliente_email', '')
        
        try:
            # Buscar si ya existe el perfil
            cliente = PerfilCliente.objects.get(dni=cliente_dni)
            
            # Actualizar datos si cambiaron
            VentaService._actualizar_datos_cliente(
                cliente, 
                cliente_nombre, 
                cliente_telefono, 
                cliente_email
            )
            
            # Si no tiene Usuario vinculado, crear uno
            if not cliente.usuario:
                VentaService._crear_usuario_para_cliente(cliente, cliente_dni, cliente_email)
        
        except PerfilCliente.DoesNotExist:
            # Crear nuevo Usuario + PerfilCliente
            cliente = VentaService._crear_nuevo_cliente(
                cliente_dni,
                cliente_nombre,
                cliente_telefono,
                cliente_email
            )
        
        return cliente
    
    @staticmethod
    def _actualizar_datos_cliente(
        cliente: PerfilCliente, 
        nombre: str, 
        telefono: str, 
        email: str
    ):
        """Actualizar datos del cliente si han cambiado"""
        actualizado = False
        
        if cliente.nombre_completo != nombre:
            cliente.nombre_completo = nombre
            actualizado = True
        
        if telefono and cliente.telefono != telefono:
            cliente.telefono = telefono
            actualizado = True
        
        if actualizado:
            cliente.save()
        
        # Actualizar email en Usuario si cambió
        if cliente.usuario and email and cliente.usuario.email != email:
            cliente.usuario.email = email
            cliente.usuario.save()
    
    @staticmethod
    def _crear_usuario_para_cliente(cliente: PerfilCliente, dni: str, email: str):
        """Crear usuario para un cliente existente que no lo tiene"""
        username = f"cliente_{dni}"
        usuario = Usuario.objects.create_user(
            username=username,
            email=email if email else f"{dni}@temp.com",
            password=dni,  # Password temporal = DNI
            rol=RolUsuario.CLIENTE
        )
        usuario.is_staff = False
        usuario.save()
        
        cliente.usuario = usuario
        cliente.save()
    
    @staticmethod
    def _crear_nuevo_cliente(dni: str, nombre: str, telefono: str, email: str) -> PerfilCliente:
        """Crear un nuevo cliente con su usuario asociado"""
        username = f"cliente_{dni}"
        
        # Crear Usuario con rol CLIENTE
        usuario = Usuario.objects.create_user(
            username=username,
            email=email if email else f"{dni}@temp.com",
            password=dni,  # Password temporal = DNI
            rol=RolUsuario.CLIENTE
        )
        usuario.is_staff = False
        usuario.save()
        
        # Crear PerfilCliente vinculado
        cliente = PerfilCliente.objects.create(
            usuario=usuario,
            dni=dni,
            nombre_completo=nombre,
            telefono=telefono
        )
        
        return cliente
    
    @staticmethod
    def _calcular_total(tickets_data: list) -> float:
        """Calcular el total de la venta basado en las zonas de los tickets"""
        total = 0
        for ticket_data in tickets_data:
            zona = Zona.objects.get(id=ticket_data['zona_id'])
            total += zona.precio
        return total
    
    @staticmethod
    def _crear_tickets(venta: Venta, tickets_data: list):
        """Crear todos los tickets de la venta con QR codes"""
        for ticket_data in tickets_data:
            try:
                ticket = Ticket.objects.create(
                    venta=venta,
                    zona_id=ticket_data['zona_id'],
                    dni_titular=ticket_data['dni_titular'],
                    nombre_titular=ticket_data['nombre_titular']
                )
                
                # Calcular validez dinámica del token basada en la fecha del evento
                validity_hours = VentaService._calcular_validez_token(ticket)
                
                # Generar QR code con ENCRIPTACIÓN AVANZADA (AES-256 + HMAC)
                qr_file, token_encriptado = QRCodeService.generar_qr(
                    codigo_uuid=ticket.codigo_uuid,
                    ticket_id=ticket.id,
                    usar_encriptacion=True,
                    validity_hours=validity_hours
                )
                
                # Guardar QR y token encriptado
                ticket.qr_image.save(f'{ticket.codigo_uuid}.png', qr_file, save=False)
                ticket.token_encriptado = token_encriptado
                ticket.save()
                
            except ValidationError as e:
                # Si un ticket falla, la transacción completa se revierte
                raise ValidationError(f'Error al crear ticket: {str(e)}')
    
    @staticmethod
    def _calcular_validez_token(ticket: Ticket) -> int:
        """
        Calcular validez del token en horas basado en la fecha del evento
        Token válido hasta 7 días después del evento
        """
        zona = ticket.zona
        evento = zona.evento
        
        if evento.fecha:
            # Token válido hasta 7 días después del evento
            dias_hasta_evento = (evento.fecha - datetime.now().date()).days
            validity_hours = max((dias_hasta_evento + 7) * 24, 24)  # Mínimo 24 horas
        else:
            # Fallback: 1 año si no hay fecha configurada
            validity_hours = 8760
        
        return validity_hours
