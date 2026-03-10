"""
Modelos de Usuario
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class RolUsuario(models.TextChoices):
    """Enumeración de roles - Principio de Open/Closed"""
    ADMIN = 'ADMIN', 'Administrador'
    VENDEDOR = 'VENDEDOR', 'Vendedor'
    VALIDADOR = 'VALIDADOR', 'Validador'
    CLIENTE = 'CLIENTE', 'Cliente'


class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para Usuario
    Responsabilidad: Creación y gestión de usuarios
    """
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('El usuario debe tener un DNI/username')
        if not email:
            raise ValueError('El usuario debe tener un email')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', RolUsuario.ADMIN)
        
        return self.create_user(username, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuario personalizado
    Responsabilidad: Representar un usuario del sistema con su rol
    """
    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='El DNI debe tener 8 dígitos'
    )
    
    username = models.CharField(
        'Usuario',
        max_length=50,
        unique=True,
        help_text='Nombre de usuario único'
    )
    email = models.EmailField('Email', unique=True)
    rol = models.CharField(
        'Rol',
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.VENDEDOR
    )
    
    # Asignación de eventos para validadores
    eventos_asignados = models.ManyToManyField(
        'eventos.Evento',
        through='ValidadorEvento',
        blank=True,
        related_name='validadores_asignados',
        verbose_name='Eventos Asignados',
        help_text='Eventos en los que este validador puede escanear tickets. Solo aplica para rol VALIDADOR.'
    )
    
    is_active = models.BooleanField('Activo', default=True)
    is_staff = models.BooleanField('Staff', default=False)
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        if hasattr(self, 'perfil_cliente') and self.perfil_cliente:
            return f'{self.perfil_cliente.nombre_completo} ({self.username})'
        return f'{self.username}'
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario (de perfil_cliente o username)"""
        if hasattr(self, 'perfil_cliente') and self.perfil_cliente:
            return self.perfil_cliente.nombre_completo
        return self.username
    
    def tiene_permiso(self, permiso: str) -> bool:
        """Verifica permisos según rol - Dependency Inversion"""
        permisos_rol = {
            RolUsuario.ADMIN: ['crear_usuario', 'ver_reportes', 'anular_tickets', 'crear_eventos'],
            RolUsuario.VENDEDOR: ['crear_ventas', 'ver_ventas'],
            RolUsuario.VALIDADOR: ['validar_tickets', 'ver_validaciones'],
            RolUsuario.CLIENTE: ['ver_mis_tickets', 'comprar_tickets'],
        }
        return permiso in permisos_rol.get(self.rol, [])
    
    def puede_validar_evento(self, evento) -> bool:
        """
        Verifica si este validador puede escanear tickets del evento especificado
        
        REGLA DE SEGURIDAD:
        - ADMIN: Puede validar en cualquier evento
        - VALIDADOR: Solo si está asignado explícitamente al evento
        - Otros roles: No pueden validar
        """
        if self.rol == RolUsuario.ADMIN:
            return True
        
        if self.rol == RolUsuario.VALIDADOR:
            return self.eventos_asignados.filter(id=evento.id).exists()
        
        return False
    
    def eventos_disponibles_para_validacion(self):
        """Retorna los eventos en los que este usuario puede validar"""
        if self.rol == RolUsuario.ADMIN:
            from apps.eventos.models import Evento
            return Evento.objects.filter(activo=True)
        elif self.rol == RolUsuario.VALIDADOR:
            return self.eventos_asignados.filter(activo=True)
        return []


class ValidadorEvento(models.Model):
    """Tabla intermedia para asignación de validadores a eventos"""
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='asignaciones_evento'
    )
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.CASCADE,
        related_name='asignaciones_validador'
    )
    fecha_asignacion = models.DateTimeField(
        'Fecha de Asignación',
        auto_now_add=True,
        help_text='Fecha en que se asignó este validador al evento'
    )
    activo = models.BooleanField(
        'Activo',
        default=True,
        help_text='Si la asignación está activa. Se desactiva automáticamente cuando el evento se desactiva'
    )
    
    class Meta:
        db_table = 'usuarios_usuario_eventos_asignados'
        verbose_name = 'Asignación Validador-Evento'
        verbose_name_plural = 'Asignaciones Validador-Evento'
        unique_together = [('usuario', 'evento')]
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f'{self.usuario.nombre_completo} → {self.evento.nombre}'


class PerfilCliente(models.Model):
    """
    Perfil de Cliente/Comprador
    Responsabilidad: Almacenar datos de personas que compran tickets
    Preparado para futuro sistema de login de clientes
    """
    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='El DNI debe tener 8 dígitos'
    )
    
    dni = models.CharField(
        'DNI',
        max_length=8,
        unique=True,
        validators=[dni_validator]
    )
    nombre_completo = models.CharField('Nombre Completo', max_length=200)
    telefono = models.CharField('Teléfono', max_length=15, blank=True)
    
    # Para futuro login de clientes
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_cliente'
    )
    
    fecha_registro = models.DateTimeField('Fecha de Registro', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Cliente'
        verbose_name_plural = 'Perfiles de Clientes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['nombre_completo']),
        ]
    
    def __str__(self):
        return f'{self.nombre_completo} - {self.dni}'
    
    def total_compras(self):
        """Retorna el total de compras realizadas"""
        return self.ventas.count()
    
    def total_tickets(self):
        """Retorna el total de tickets que tiene como titular"""
        from apps.ventas.models import Ticket
        return Ticket.objects.filter(dni_titular=self.dni).count()
