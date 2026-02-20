"""
Modelos de Eventos y Zonas
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class Categoria(models.Model):

    """
    Categoría de Evento
    """
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=120, unique=True)
    imagen_path = models.ImageField('Imagen', upload_to='eventos/categorias/', blank=True, null=True)
    estado = models.CharField('Estado', max_length=1, choices=[('1', 'Activo'), ('2', 'Desactivado')], default='1')
    activo = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
        
    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug and self.nombre:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

class Presentacion(models.Model):
    """
    Presentación de un Evento (fecha y hora específica)
    """
    evento = models.ForeignKey('Evento', on_delete=models.CASCADE, related_name='presentaciones')
    fecha = models.DateField('Fecha')
    hora_inicio = models.TimeField('Hora de Inicio')
    descripcion = models.CharField('Descripción', max_length=200, blank=True)
    class Meta:
        verbose_name = 'Presentación'
        verbose_name_plural = 'Presentaciones'
        ordering = ['evento', 'fecha', 'hora_inicio']
    def __str__(self):
        return f'{self.evento.nombre} - {self.fecha} {self.hora_inicio}'

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
    
    nombre = models.CharField('Nombre', max_length=200, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, related_name='eventos')
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
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['activo', 'fecha_creacion']),
        ]
    def __str__(self):
        return f'{self.nombre}'
    def total_presentaciones(self):
        return self.presentaciones.count()
    def total_zonas(self):
        return sum(p.zonas.count() for p in self.presentaciones.all())

class Zona(models.Model):
    """
    Modelo de Zona dentro de un Evento
    Responsabilidad: Gestionar capacidad y precio de una zona específica
    """
    presentacion = models.ForeignKey(
        Presentacion,
        on_delete=models.CASCADE,
        related_name='zonas',
        verbose_name='Presentación'
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
        ordering = ['presentacion', 'precio']
        unique_together = [['presentacion', 'nombre']]
        indexes = [
            models.Index(fields=['presentacion', 'activo']),
        ]
    def __str__(self):
        return f'{self.presentacion} - {self.nombre} (S/ {self.precio})'
    def tickets_vendidos(self):
        from apps.ventas.models import EstadoTicket
        return self.tickets.filter(estado=EstadoTicket.ACTIVO).count()
    def tickets_disponibles(self):
        return self.capacidad_maxima - self.tickets_vendidos()
    def tiene_disponibilidad(self, cantidad: int = 1) -> bool:
        return self.tickets_disponibles() >= cantidad
    def porcentaje_ocupacion(self):
        if self.capacidad_maxima == 0:
            return 0
        return round((self.tickets_vendidos() / self.capacidad_maxima) * 100, 2)
    def clean(self):
        if self.capacidad_maxima <= 0:
            raise ValidationError('La capacidad máxima debe ser mayor a 0')
        if self.precio < 0:
            raise ValidationError('El precio no puede ser negativo')
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
