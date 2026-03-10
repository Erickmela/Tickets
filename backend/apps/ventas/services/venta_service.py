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
        
        # Paso 2: Calcular montos (subtotal, comisión, total)
        montos = VentaService._calcular_montos(tickets_data)
        
        # Paso 3: Crear la venta
        venta = Venta.objects.create(
            vendedor=vendedor,
            cliente_pagador=cliente,
            subtotal=montos['subtotal'],
            comision=montos['comision'],
            total_pagado=montos['total'],
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
    def _calcular_montos(tickets_data: list) -> dict:
        """
        Calcular subtotal, comisión y total basado en los tickets
        La comisión se calcula por cada entrada individual según la configuración del evento
        
        Returns:
            dict: {
                'subtotal': Decimal,  # Suma de precios de tickets
                'comision': Decimal,  # Comisión total (suma de comisiones por ticket)
                'total': Decimal      # subtotal + comision
            }
        """
        from decimal import Decimal
        
        subtotal = Decimal('0.00')
        comision_total = Decimal('0.00')
        
        # Obtener el evento desde el primer ticket (todos deben ser del mismo evento)
        if not tickets_data:
            raise ValidationError('Debe incluir al menos un ticket')
        
        # Obtener zona y evento del primer ticket
        primera_zona = Zona.objects.select_related(
            'presentacion__evento'
        ).get(id=tickets_data[0]['zona_id'])
        evento = primera_zona.presentacion.evento
        
        # Calcular por cada ticket
        for ticket_data in tickets_data:
            zona = Zona.objects.get(id=ticket_data['zona_id'])
            precio_ticket = Decimal(str(zona.precio))
            
            # Acumular subtotal
            subtotal += precio_ticket
            
            # Calcular comisión de este ticket si no está incluida en el precio
            if not evento.comision_incluida_precio and evento.comision_porcentaje > 0:
                comision_ticket = precio_ticket * (Decimal(str(evento.comision_porcentaje)) / Decimal('100'))
                comision_total += comision_ticket.quantize(Decimal('0.01'))
        
        total = subtotal + comision_total
        
        return {
            'subtotal': subtotal,
            'comision': comision_total,
            'total': total
        }
    
    @staticmethod
    def _crear_tickets(venta: Venta, tickets_data: list):
        """Crear todos los tickets de la venta con QR codes"""
        for ticket_data in tickets_data:
            try:
                ticket = Ticket.objects.create(
                    venta=venta,
                    presentacion_id=ticket_data['presentacion_id'],
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
        Calcular validez del token en horas basado en la fecha de la presentación
        Token válido hasta 7 días después de la presentación
        """
        presentacion = ticket.presentacion
        
        if presentacion and presentacion.fecha:
            # Token válido hasta 7 días después de la presentación
            dias_hasta = (presentacion.fecha - datetime.now().date()).days
            validity_hours = max((dias_hasta + 7) * 24, 24)  # Mínimo 24 horas
        else:
            # Fallback: 1 año si no hay presentación
            validity_hours = 8760
        
        return validity_hours
