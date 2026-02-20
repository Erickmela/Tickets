"""
Modelos de Ventas y Tickets
"""
import uuid
from pathlib import Path
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from apps.usuarios.models import Usuario, PerfilCliente
from apps.eventos.models import Zona, Presentacion


class MetodoPago(models.TextChoices):
    """Enumeración de métodos de pago - Open/Closed Principle"""
    EFECTIVO = 'EFECTIVO', 'Efectivo'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia Bancaria'
    YAPE = 'YAPE', 'Yape'
    PLIN = 'PLIN', 'Plin'
    TARJETA = 'TARJETA', 'Tarjeta'


class EstadoTicket(models.TextChoices):
    """Estados del ciclo de vida de un ticket"""
    ACTIVO = 'ACTIVO', 'Activo'
    USADO = 'USADO', 'Usado'
    ANULADO = 'ANULADO', 'Anulado'


class Orden(models.Model):
    cliente = models.ForeignKey(PerfilCliente, on_delete=models.PROTECT, related_name='ordenes')
    fecha_orden = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    mp_payment_id = models.CharField(max_length=50, blank=True, null=True)
    mp_status = models.CharField(max_length=50, blank=True, null=True)
    mp_status_detail = models.CharField(max_length=100, blank=True, null=True)
    mp_payment_method_id = models.CharField(max_length=50, blank=True, null=True)
    mp_payment_type = models.CharField(max_length=50, blank=True, null=True)
    mp_preference_id = models.CharField(max_length=50, blank=True, null=True)
    mp_merchant_order_id = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente')
    observaciones = models.TextField(blank=True)
    def __str__(self):
        return f'Orden #{self.pk} - {self.cliente.nombre_completo}'

class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

class Carrito(models.Model):
    cliente = models.ForeignKey(PerfilCliente, on_delete=models.CASCADE, related_name='carritos')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)

class Venta(models.Model):
    """
    Modelo de Venta (Transacción)
    Responsabilidad: Registrar la transacción comercial
    """
    vendedor = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='ventas_realizadas',
        verbose_name='Vendedor',
        limit_choices_to={'rol': 'VENDEDOR'}
    )
    cliente_pagador = models.ForeignKey(
        PerfilCliente,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Cliente que Paga'
    )
    fecha_venta = models.DateTimeField('Fecha de Venta', auto_now_add=True)
    total_pagado = models.DecimalField('Total Pagado', max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(
        'Método de Pago',
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO
    )
    nro_operacion = models.CharField(
        'Nro de Operación',
        max_length=50,
        blank=True,
        help_text='Número de operación bancaria o código de transacción'
    )
    observaciones = models.TextField('Observaciones', blank=True)
    activo = models.BooleanField('Activo', default=True)
    orden = models.ForeignKey(Orden, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
        indexes = [
            models.Index(fields=['-fecha_venta']),
            models.Index(fields=['vendedor', '-fecha_venta']),
            models.Index(fields=['cliente_pagador']),
        ]
    
    def __str__(self):
        return f'Venta #{self.pk} - {self.cliente_pagador.nombre_completo} - S/ {self.total_pagado}'
    
    def cantidad_tickets(self):
        """Retorna la cantidad de tickets de esta venta"""
        return self.tickets.count()
    
    def tickets_activos(self):
        """Retorna la cantidad de tickets activos"""
        return self.tickets.filter(estado=EstadoTicket.ACTIVO).count()
    
    def puede_anularse(self) -> bool:
        """Verifica si la venta puede anularse - ningún ticket debe estar usado"""
        return not self.tickets.filter(estado=EstadoTicket.USADO).exists()


class Ticket(models.Model):
    """
    Modelo de Ticket (Acceso al Evento)
    SEGURIDAD: Usa UUID4 para prevenir clonación
    """
    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='El DNI debe tener 8 dígitos'
    )
    
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Venta'
    )
    presentacion = models.ForeignKey(
        Presentacion,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Presentación'
    )
    zona = models.ForeignKey(
        Zona,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Zona'
    )
    
    # Información del Titular (persona que ingresará con este ticket)
    dni_titular = models.CharField(
        'DNI del Titular',
        max_length=8,
        validators=[dni_validator],
        help_text='DNI de la persona que usará este ticket'
    )
    nombre_titular = models.CharField('Nombre del Titular', max_length=200)
    
    # SEGURIDAD ANTI-CLONACIÓN: UUID4
    codigo_uuid = models.UUIDField(
        'Código UUID',
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text='Código único imposible de clonar'
    )
    
    # SEGURIDAD AVANZADA: Token encriptado AES-256 + HMAC
    token_encriptado = models.TextField(
        'Token Encriptado',
        blank=True,
        help_text='Token con UUID encriptado usando AES-256 + HMAC para máxima seguridad'
    )
    
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=EstadoTicket.choices,
        default=EstadoTicket.ACTIVO
    )
    
    qr_image = models.ImageField(
        'Código QR',
        upload_to='qr_codes/',
        null=True,
        blank=True
    )
    
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['codigo_uuid']),
            models.Index(fields=['dni_titular']),
            models.Index(fields=['estado']),
            models.Index(fields=['zona', 'estado']),
        ]
    
    def __str__(self):
        return f'Ticket #{self.pk} - {self.nombre_titular} - {self.zona.nombre}'
    
    def save(self, *args, **kwargs):
        """
        Override save para validaciones antes de guardar
        Aplicando validaciones de negocio centralizadas
        """
        if not self.pk:  # Solo en creación
            self._validar_limite_titular()
            self._validar_disponibilidad_zona()
        super().save(*args, **kwargs)
    
    def _validar_limite_titular(self):
        """
        REGLA DE NEGOCIO: Máximo 3 tickets por titular por evento
        Previene acaparamiento de entradas
        """
        evento = self.zona.evento
        tickets_titular = Ticket.objects.filter(
            dni_titular=self.dni_titular,
            zona__evento=evento,
            estado=EstadoTicket.ACTIVO
        ).count()
        
        if tickets_titular >= 3:
            raise ValidationError(
                f'El titular con DNI {self.dni_titular} ya tiene 3 tickets para este evento. '
                f'No se pueden vender más.'
            )
    
    def _validar_disponibilidad_zona(self):
        """
        REGLA DE NEGOCIO: Validar que la zona tenga disponibilidad
        Control de aforo estricto
        """
        if not self.zona.tiene_disponibilidad():
            raise ValidationError(
                f'La zona {self.zona.nombre} ha alcanzado su capacidad máxima. '
                f'No hay tickets disponibles.'
            )
    
    def puede_usarse(self) -> bool:
        """
        Verifica si el ticket puede ser usado para ingresar
        Responsabilidad única: validar estado
        """
        return self.estado == EstadoTicket.ACTIVO
    
    def marcar_como_usado(self):
        """
        Marca el ticket como usado después de validación exitosa
        Transición de estado controlada
        """
        if not self.puede_usarse():
            raise ValidationError(f'Este ticket no puede ser usado. Estado actual: {self.get_estado_display()}')
        
        self.estado = EstadoTicket.USADO
        self.save(update_fields=['estado', 'fecha_actualizacion'])
    
    def anular(self, motivo: str = ''):
        """
        Anula el ticket
        Solo posible si no ha sido usado
        """
        if self.estado == EstadoTicket.USADO:
            raise ValidationError('No se puede anular un ticket que ya fue usado')
        
        self.estado = EstadoTicket.ANULADO
        if motivo:
            self.venta.observaciones += f'\nTicket #{self.pk} anulado: {motivo}'
            self.venta.save(update_fields=['observaciones'])
        self.save(update_fields=['estado', 'fecha_actualizacion'])
