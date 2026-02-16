"""
Modelo de Validaciones - Control de Acceso
Responsabilidad: Registrar cada ingreso al evento
"""
from django.db import models
from django.core.exceptions import ValidationError
from apps.ventas.models import Ticket
from apps.usuarios.models import Usuario


class Validacion(models.Model):
    """
    Modelo de Validación de Ingreso
    Responsabilidad: Registrar el momento exacto en que un ticket fue usado
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.PROTECT,
        related_name='validaciones',
        verbose_name='Ticket'
    )
    validador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='validaciones_realizadas',
        verbose_name='Validador',
        limit_choices_to={'rol': 'VALIDADOR'}
    )
    
    fecha_hora_ingreso = models.DateTimeField('Fecha y Hora de Ingreso', auto_now_add=True)
    observaciones = models.TextField('Observaciones', blank=True)
    
    # Información de auditoría
    ip_address = models.GenericIPAddressField('Dirección IP', null=True, blank=True)
    dispositivo = models.CharField('Dispositivo', max_length=200, blank=True)
    
    class Meta:
        verbose_name = 'Validación de Ingreso'
        verbose_name_plural = 'Validaciones de Ingreso'
        ordering = ['-fecha_hora_ingreso']
        indexes = [
            models.Index(fields=['-fecha_hora_ingreso']),
            models.Index(fields=['ticket']),
            models.Index(fields=['validador', '-fecha_hora_ingreso']),
        ]
    
    def __str__(self):
        return f'Validación #{self.pk} - {self.ticket.nombre_titular} - {self.fecha_hora_ingreso}'
    
    def save(self, *args, **kwargs):
        """
        Override save para validar y marcar el ticket como usado
        Aplicando transaccionalidad
        """
        if not self.pk:  # Solo en creación
            self._validar_ticket()
            # Marcar el ticket como usado
            self.ticket.marcar_como_usado()
        super().save(*args, **kwargs)
    
    def _validar_ticket(self):
        """
        Valida que el ticket pueda ser usado
        REGLA DE NEGOCIO: Un ticket solo puede usarse una vez
        """
        if not self.ticket.puede_usarse():
            # Buscar la validación previa para mostrar cuándo se usó
            validacion_previa = Validacion.objects.filter(ticket=self.ticket).first()
            if validacion_previa:
                raise ValidationError(
                    f'Este ticket ya fue usado el {validacion_previa.fecha_hora_ingreso.strftime("%d/%m/%Y a las %H:%M:%S")} '
                    f'por el validador {validacion_previa.validador.nombre_completo}'
                )
            else:
                raise ValidationError(f'Este ticket no puede ser usado. Estado: {self.ticket.get_estado_display()}')
