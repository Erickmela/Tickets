"""
Modelos de Eventos y Zonas
"""
from django.db import models
from django.core.exceptions import ValidationError


class Evento(models.Model):
    """
    Modelo de Evento
    """
    ESTADO_CHOICES = [
        ('1', 'Próximo'),
        ('2', 'Activo'),
        ('3', 'Finalizado'),
    ]
    
    REGION_CHOICES = [
        ('Lima', 'Lima'),
        ('Arequipa', 'Arequipa'),
        ('Cusco', 'Cusco'),
        ('La Libertad', 'La Libertad'),
        ('Piura', 'Piura'),
        ('Lambayeque', 'Lambayeque'),
        ('Junín', 'Junín'),
        ('Puno', 'Puno'),
        ('Ica', 'Ica'),
        ('Áncash', 'Áncash'),
        ('Cajamarca', 'Cajamarca'),
        ('Loreto', 'Loreto'),
        ('San Martín', 'San Martín'),
        ('Ucayali', 'Ucayali'),
        ('Huánuco', 'Huánuco'),
        ('Ayacucho', 'Ayacucho'),
        ('Tacna', 'Tacna'),
        ('Moquegua', 'Moquegua'),
        ('Amazonas', 'Amazonas'),
        ('Apurímac', 'Apurímac'),
        ('Huancavelica', 'Huancavelica'),
        ('Madre de Dios', 'Madre de Dios'),
        ('Pasco', 'Pasco'),
        ('Tumbes', 'Tumbes'),
        ('Callao', 'Callao'),
    ]
    
    CATEGORIA_CHOICES = [
        ('Música', 'Música'),
        ('Deportes', 'Deportes'),
        ('Teatro', 'Teatro'),
        ('Conferencias', 'Conferencias'),
        ('Festivales', 'Festivales'),
        ('Gastronomía', 'Gastronomía'),
        ('Infantiles', 'Infantiles'),
        ('Otros', 'Otros'),
    ]
    
    nombre = models.CharField('Nombre', max_length=200, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    categoria = models.CharField('Categoría', max_length=50, choices=CATEGORIA_CHOICES, default='Otros')
    fecha = models.DateField('Fecha del Evento')
    hora_inicio = models.TimeField('Hora de Inicio', null=True, blank=True)
    lugar = models.CharField('Lugar', max_length=300, blank=True, help_text='Dirección exacta del evento')
    region = models.CharField('Región', max_length=50, choices=REGION_CHOICES, default='Lima', help_text='Región donde se realiza el evento')
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='1')
    activo = models.BooleanField('Activo', default=False, help_text='Solo un evento puede estar activo')
    
    # Imágenes del evento
    imagen_principal = models.ImageField(
        'Imagen Principal',
        upload_to='eventos/principal/',
        blank=True,
        null=True,
        help_text='Imagen principal del evento (portada)'
    )
    imagen_flyer = models.ImageField(
        'Flyer',
        upload_to='eventos/flyers/',
        blank=True,
        null=True,
        help_text='Flyer promocional del evento'
    )
    imagen_banner = models.ImageField(
        'Banner',
        upload_to='eventos/banners/',
        blank=True,
        null=True,
        help_text='Banner para header o slider'
    )
    imagen_cartel = models.ImageField(
        'Cartel',
        upload_to='eventos/carteles/',
        blank=True,
        null=True,
        help_text='Cartel o póster del evento'
    )
    imagen_mapa_zonas = models.ImageField(
        'Mapa de Zonas',
        upload_to='eventos/mapas/',
        blank=True,
        null=True,
        help_text='Plano/mapa con la distribución de zonas del local (VIP, General, etc.)'
    )
    
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['activo', 'fecha']),
        ]
    
    def __str__(self):
        return f'{self.nombre} - {self.fecha}'
    
    def clean(self):
        """
        Validación: Solo un evento puede estar en estado ACTIVO a la vez
        Principio de validación centralizada
        """
        if self.estado == '2':  # ACTIVO
            eventos_activos = Evento.objects.filter(estado='2')
            if self.pk:
                eventos_activos = eventos_activos.exclude(pk=self.pk)
            if eventos_activos.exists():
                raise ValidationError('Ya existe un evento en estado ACTIVO. Cámbialo a otro estado antes de activar este.')
    
    def save(self, *args, **kwargs):
        # Sincronizar campo activo con estado
        self.activo = (self.estado == '2')
        self.full_clean()
        super().save(*args, **kwargs)
    
    def total_zonas(self):
        """Retorna el número de zonas del evento"""
        return self.zonas.count()
    
    def capacidad_total(self):
        """Retorna la capacidad total del evento"""
        return self.zonas.aggregate(
            total=models.Sum('capacidad_maxima')
        )['total'] or 0
    
    def tickets_vendidos(self):
        """Retorna el total de tickets vendidos para este evento"""
        from apps.ventas.models import Ticket, EstadoTicket
        return Ticket.objects.filter(
            zona__evento=self,
            estado=EstadoTicket.ACTIVO
        ).count()
    
    def disponibilidad(self):
        """Porcentaje de disponibilidad del evento"""
        capacidad = self.capacidad_total()
        if capacidad == 0:
            return 0
        vendidos = self.tickets_vendidos()
        return round((1 - vendidos / capacidad) * 100, 2)


class Zona(models.Model):
    """
    Modelo de Zona dentro de un Evento
    Responsabilidad: Gestionar capacidad y precio de una zona específica
    """
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='zonas',
        verbose_name='Evento'
    )
    nombre = models.CharField('Nombre', max_length=100, help_text='Ej: VIP, General, Palco')
    descripcion = models.TextField('Descripción', blank=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    capacidad_maxima = models.PositiveIntegerField(
        'Capacidad Máxima',
        help_text='Número máximo de personas en esta zona'
    )
    activo = models.BooleanField('Activo', default=True)
    
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'
        ordering = ['evento', 'precio']
        unique_together = [['evento', 'nombre']]
        indexes = [
            models.Index(fields=['evento', 'activo']),
        ]
    
    def __str__(self):
        return f'{self.evento.nombre} - {self.nombre} (S/ {self.precio})'
    
    def tickets_vendidos(self):
        """
        Retorna el número de tickets vendidos en esta zona
        Responsabilidad única: contar tickets activos
        """
        from apps.ventas.models import EstadoTicket
        return self.tickets.filter(estado=EstadoTicket.ACTIVO).count()
    
    def tickets_disponibles(self):
        """Retorna el número de tickets disponibles"""
        return self.capacidad_maxima - self.tickets_vendidos()
    
    def tiene_disponibilidad(self, cantidad: int = 1) -> bool:
        """
        Verifica si hay disponibilidad para una cantidad de tickets
        Encapsulación de lógica de negocio
        """
        return self.tickets_disponibles() >= cantidad
    
    def porcentaje_ocupacion(self):
        """Retorna el porcentaje de ocupación de la zona"""
        if self.capacidad_maxima == 0:
            return 0
        return round((self.tickets_vendidos() / self.capacidad_maxima) * 100, 2)
    
    def clean(self):
        """Validación de capacidad"""
        if self.capacidad_maxima <= 0:
            raise ValidationError('La capacidad máxima debe ser mayor a 0')
        if self.precio < 0:
            raise ValidationError('El precio no puede ser negativo')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
