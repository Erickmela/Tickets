"""
Serializers para Usuarios - Arquitectura Unificada
Todo el mundo tiene Usuario + PerfilCliente, diferenciados por rol
"""
from rest_framework import serializers
from .models import Usuario, PerfilCliente, RolUsuario
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction


class UsuarioConPerfilSerializer(serializers.ModelSerializer):
    """Serializer para leer Usuario con su Perfil"""
    activo = serializers.BooleanField(source='is_active', read_only=True)
    usuario = serializers.CharField(source='username', read_only=True)
    dni = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'usuario', 'username', 'dni', 'email', 'nombre_completo', 
                  'telefono', 'rol', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_dni(self, obj):
        """Obtener DNI del perfil cliente"""
        try:
            return obj.perfil_cliente.dni if hasattr(obj, 'perfil_cliente') else ''
        except:
            return ''
    
    def get_telefono(self, obj):
        """Obtener teléfono del perfil cliente"""
        try:
            return obj.perfil_cliente.telefono if hasattr(obj, 'perfil_cliente') else ''
        except:
            return ''
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del perfil cliente"""
        try:
            return obj.perfil_cliente.nombre_completo if hasattr(obj, 'perfil_cliente') else ''
        except:
            return ''


class TrabajadorCreateSerializer(serializers.Serializer):
    """Serializer para crear trabajadores - Crea Usuario + PerfilCliente"""
    usuario = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirmation = serializers.CharField(write_only=True, min_length=6)
    dni = serializers.CharField(max_length=8, min_length=8)
    nombre_completo = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    telefono = serializers.CharField(max_length=15, required=False, allow_blank=True)
    rol = serializers.ChoiceField(choices=RolUsuario.choices)
    
    def validate_usuario(self, value):
        """Validar que el username sea único"""
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso")
        return value
    
    def validate_dni(self, value):
        """Validar formato DNI"""
        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError("El DNI debe tener 8 dígitos numéricos")
        
        if PerfilCliente.objects.filter(dni=value).exists():
            raise serializers.ValidationError("Ya existe un perfil con este DNI")
        
        return value
    
    def validate_email(self, value):
        """Validar email único"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está en uso")
        return value
    
    def validate_rol(self, value):
        """Validar que el rol no sea CLIENTE"""
        if value == RolUsuario.CLIENTE:
            raise serializers.ValidationError("Use el endpoint de clientes para crear clientes")
        return value
    
    def validate(self, data):
        """Validación cruzada"""
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({'password_confirmation': 'Las contraseñas no coinciden'})
        
        # Validar fortaleza de contraseña
        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        password_confirmation = validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        usuario = validated_data.pop('usuario')
        dni = validated_data.pop('dni')
        nombre_completo = validated_data.pop('nombre_completo')
        email = validated_data.pop('email')
        telefono = validated_data.pop('telefono', '')
        rol = validated_data.pop('rol')
        
        # Crear Usuario
        user = Usuario.objects.create_user(
            username=usuario,
            email=email,
            password=password,
            rol=rol
        )
        user.is_staff = True  # Los trabajadores son staff
        user.save()
        
        # Crear PerfilCliente vinculado
        perfil = PerfilCliente.objects.create(
            usuario=user,
            dni=dni,
            nombre_completo=nombre_completo,
            telefono=telefono
        )
        
        return user


class TrabajadorUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar trabajadores - Actualiza Usuario + PerfilCliente"""
    usuario = serializers.CharField(max_length=50, required=False)
    password = serializers.CharField(write_only=True, min_length=6, required=False, allow_blank=True)
    password_confirmation = serializers.CharField(write_only=True, min_length=6, required=False, allow_blank=True)
    dni = serializers.CharField(max_length=8, min_length=8, required=False)
    nombre_completo = serializers.CharField(max_length=200, required=False)
    email = serializers.EmailField(required=False)
    telefono = serializers.CharField(max_length=15, required=False, allow_blank=True)
    rol = serializers.ChoiceField(choices=RolUsuario.choices, required=False)
    
    def validate_dni(self, value):
        """Validar formato DNI"""
        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError("El DNI debe tener 8 dígitos numéricos")
        return value
    
    def validate(self, data):
        """Validación cruzada"""
        password = data.get('password', '')
        password_confirmation = data.get('password_confirmation', '')
        
        # Si se proporciona contraseña, validarla
        if password or password_confirmation:
            if password != password_confirmation:
                raise serializers.ValidationError({'password_confirmation': 'Las contraseñas no coinciden'})
            
            if password:
                try:
                    validate_password(password)
                except DjangoValidationError as e:
                    raise serializers.ValidationError({'password': list(e.messages)})
        
        return data
    
    @transaction.atomic
    def update(self, instance, validated_data):
        password_confirmation = validated_data.pop('password_confirmation', None)
        password = validated_data.pop('password', None)
        dni = validated_data.pop('dni', None)
        nombre_completo = validated_data.pop('nombre_completo', None)
        telefono = validated_data.pop('telefono', None)
        usuario = validated_data.pop('usuario', None)
        email = validated_data.get('email', None)
        rol = validated_data.get('rol', None)
        
        # Actualizar Usuario
        if usuario:
            instance.username = usuario
        if email:
            instance.email = email
        if rol:
            instance.rol = rol
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Actualizar PerfilCliente
        if hasattr(instance, 'perfil_cliente'):
            perfil = instance.perfil_cliente
            if dni:
                perfil.dni = dni
            if nombre_completo:
                perfil.nombre_completo = nombre_completo
            if telefono is not None:
                perfil.telefono = telefono
            perfil.save()
        
        return instance


class ClienteCreateSerializer(serializers.Serializer):
    """Serializer para crear clientes - Crea Usuario (rol=CLIENTE) + PerfilCliente
    
    Flujo de registro rápido:
    - Registro: DNI + email + password (mínimo necesario)
    - Completar Perfil: nombre_completo + telefono (después del primer login)
    """
    dni = serializers.CharField(max_length=8, min_length=8)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirmation = serializers.CharField(write_only=True, min_length=6)
    nombre_completo = serializers.CharField(max_length=200, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=15, required=False, allow_blank=True)
    
    def validate_dni(self, value):
        """Validar formato DNI"""
        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError("El DNI debe tener 8 dígitos numéricos")
        
        if PerfilCliente.objects.filter(dni=value).exists():
            raise serializers.ValidationError("Ya existe un cliente con este DNI")
        
        return value
    
    def validate_email(self, value):
        """Validar email único"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está en uso")
        return value
    
    def validate(self, data):
        """Validación cruzada"""
        if data.get('password') != data.get('password_confirmation'):
            raise serializers.ValidationError({'password_confirmation': 'Las contraseñas no coinciden'})
        
        # Validar fortaleza de contraseña
        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        dni = validated_data['dni']
        email = validated_data['email']
        password = validated_data['password']
        password_confirmation = validated_data.pop('password_confirmation', None)
        nombre_completo = validated_data.get('nombre_completo', '')
        telefono = validated_data.get('telefono', '')
        
        # Crear Usuario con rol CLIENTE
        username = f"cliente_{dni}"  # Username generado del DNI
        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,  # Password del usuario (NO el DNI)
            rol=RolUsuario.CLIENTE
        )
        user.is_staff = False  # Los clientes no son staff
        user.save()
        
        # Crear PerfilCliente vinculado (nombre_completo y telefono pueden estar vacíos)
        perfil = PerfilCliente.objects.create(
            usuario=user,
            dni=dni,
            nombre_completo=nombre_completo,
            telefono=telefono
        )
        
        return perfil


class ClienteUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar clientes - Actualiza PerfilCliente"""
    dni = serializers.CharField(max_length=8, min_length=8, required=False)
    nombre_completo = serializers.CharField(max_length=200, required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=15, required=False, allow_blank=True)
    
    def validate_dni(self, value):
        """Validar formato DNI"""
        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError("El DNI debe tener 8 dígitos numéricos")
        return value
    
    def validate_nombre_completo(self, value):
        """Validar que el nombre no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre completo es requerido")
        return value.strip()
    
    @transaction.atomic
    def update(self, instance, validated_data):
        # Actualizar PerfilCliente
        for field in ['dni', 'nombre_completo', 'email', 'telefono']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        
        instance.save()
        
        # Actualizar Usuario vinculado si existe
        if instance.usuario and 'email' in validated_data:
            instance.usuario.email = validated_data['email']
            instance.usuario.save()
        
        return instance


class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para login - Acepta username O DNI"""
    username = serializers.CharField(
        help_text="Puede ser username (trabajadores) o DNI (clientes)"
    )
    password = serializers.CharField(write_only=True)


class PerfilClienteSerializer(serializers.ModelSerializer):
    """Serializer simple para Perfil de Cliente (solo lectura)"""
    total_compras = serializers.IntegerField(read_only=True)
    total_tickets = serializers.IntegerField(read_only=True)
    fecha_creacion = serializers.DateTimeField(source='fecha_registro', read_only=True)
    email = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    activo = serializers.SerializerMethodField()
    
    class Meta:
        model = PerfilCliente
        fields = ['id', 'dni', 'nombre_completo', 'telefono', 'email', 'rol', 'activo',
                  'fecha_creacion', 'total_compras', 'total_tickets']
        read_only_fields = ['fecha_creacion']
    
    def get_email(self, obj):
        """Obtener email del Usuario vinculado"""
        return obj.usuario.email if obj.usuario else ''
    
    def get_rol(self, obj):
        """Obtener rol del Usuario vinculado"""
        return obj.usuario.rol if obj.usuario else 'CLIENTE'
    
    def get_activo(self, obj):
        """Obtener estado activo del Usuario vinculado"""
        return obj.usuario.is_active if obj.usuario else False
    
    def to_representation(self, instance):
        """Agregar campos calculados"""
        representation = super().to_representation(instance)
        representation['total_compras'] = instance.total_compras()
        representation['total_tickets'] = instance.total_tickets()
        return representation

