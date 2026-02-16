# Sistema de Tickets "Jala Jala" - Backend

Sistema de gestión de tickets con seguridad anti-clonación desarrollado con Django REST Framework.

## 🏗️ Arquitectura y Principios SOLID

Este proyecto está desarrollado siguiendo los principios SOLID:

- **S**ingle Responsibility: Cada modelo, servicio y vista tiene una única responsabilidad
- **O**pen/Closed: Uso de enumeraciones y clases abstractas para extensibilidad
- **L**iskov Substitution: Interfaces consistentes en toda la aplicación
- **I**nterface Segregation: APIs y serializers específicos por caso de uso
- **D**ependency Inversion: Servicios de negocio independientes de la capa de datos

## 📁 Estructura del Proyecto

```
backend/
├── config/                 # Configuración del proyecto Django
│   ├── settings.py        # Settings con variables de entorno
│   └── urls.py            # URLs principales
├── apps/
│   ├── usuarios/          # Módulo de usuarios y autenticación
│   │   ├── models.py      # Usuario (Custom), PerfilCliente
│   │   ├── serializers.py # Serializers específicos por caso de uso
│   │   └── views.py       # ViewSets y vistas de autenticación
│   ├── eventos/           # Módulo de eventos y zonas
│   │   ├── models.py      # Evento, Zona (con validación de aforo)
│   │   ├── serializers.py # Serializers con datos calculados
│   │   └── views.py       # APIs para gestión de eventos
│   ├── ventas/            # Módulo de ventas y tickets
│   │   ├── models.py      # Venta, Ticket (con UUID y QR)
│   │   ├── services.py    # Servicios de negocio (VentaService, QRCodeService)
│   │   ├── serializers.py # Serializers transaccionales
│   │   └── views.py       # APIs para creación de ventas
│   └── validaciones/      # Módulo de control de acceso
│       ├── models.py      # Validacion (registro de ingresos)
│       ├── serializers.py # Serializers para validación
│       └── views.py       # API crítica de validación en puerta
└── manage.py
```

## 🔒 Características de Seguridad

### Anti-Clonación
- Cada ticket tiene un **UUID4 único** imposible de adivinar
- Código QR generado con el UUID
- Validación de uso único en base de datos

### Anti-Hackeo
- Validación a nivel de modelo con `clean()` y `save()`
- Transacciones atómicas para ventas múltiples
- Registro de auditoría en todas las validaciones

### Anti-Reventa
- Tickets nominativos con DNI y nombre
- Verificación física obligatoria en puerta
- Límite de 3 tickets por persona por evento

### Control de Aforo
- Validación estricta de capacidad por zona
- Bloqueo automático cuando se alcanza el límite
- No se puede vender más tickets de los disponibles

## 🚀 Instalación

### 1. Crear entorno virtual
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copiar `.env.example` a `.env` y configurar:
```env
SECRET_KEY=tu-secret-key-seguro
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Crear la base de datos
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario
```powershell
python manage.py createsuperuser
```

### 6. Crear directorios para archivos
```powershell
mkdir media\qr_codes
```

### 7. Ejecutar servidor
```powershell
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación de la API

Una vez iniciado el servidor, la documentación interactiva está disponible en:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

## 🔑 Endpoints Principales

### Autenticación
- `POST /api/usuarios/login/` - Iniciar sesión
- `POST /api/usuarios/logout/` - Cerrar sesión
- `GET /api/usuarios/me/` - Obtener usuario actual

### Eventos
- `GET /api/eventos/eventos/` - Listar eventos
- `GET /api/eventos/eventos/evento_activo/` - Obtener evento activo
- `GET /api/eventos/zonas/zonas_disponibles/` - Zonas con disponibilidad

### Ventas
- `POST /api/ventas/crear-venta/` - Crear venta con múltiples tickets
- `GET /api/ventas/ventas/` - Listar ventas
- `GET /api/ventas/tickets/por_dni/?dni=12345678` - Buscar tickets por DNI

### Validaciones (Puerta)
- `POST /api/validaciones/validar-ticket/` - **ENDPOINT CRÍTICO**: Validar ticket escaneado
- `GET /api/validaciones/validaciones/` - Historial de validaciones
- `GET /api/validaciones/validaciones/estadisticas/` - Estadísticas de ingreso

## 📋 Reglas de Negocio

### Límite de Tickets por Titular
```python
# Máximo 3 tickets por DNI por evento
if tickets_titular >= 3:
    raise ValidationError('Límite de 3 tickets alcanzado')
```

### Validación de Aforo
```python
# No se puede vender si la zona está llena
if not self.zona.tiene_disponibilidad():
    raise ValidationError('Zona llena')
```

### Un Solo Uso
```python
# Un ticket solo puede usarse una vez
if self.estado == 'USADO':
    raise ValidationError('Ticket ya usado')
```

### Transaccionalidad
```python
@transaction.atomic
def crear_venta(...):
    # Si falla un ticket, se revierten todos
```

## 🎯 Flujos de Trabajo

### Flujo de Venta
1. Vendedor ingresa DNI del comprador
2. Sistema autocompleta datos si existe
3. Vendedor selecciona zona y cantidad
4. Ingresa datos de cada titular (DNI y nombre)
5. Sistema valida:
   - Stock disponible
   - Límite de 3 tickets por DNI
6. Crea venta y genera tickets con QR
7. QR se puede imprimir o enviar por WhatsApp

### Flujo de Validación (Puerta)
1. Validador escanea QR con celular
2. App envía UUID al servidor
3. Servidor valida:
   - Ticket existe (UUID válido)
   - Estado es ACTIVO
   - No ha sido usado antes
4. Si es válido:
   - Muestra: ✅ ACCESO PERMITIDO
   - Datos: Nombre y DNI para verificar
   - Marca ticket como USADO
5. Si ya fue usado:
   - Muestra: ❌ TICKET YA USADO
   - Fecha y hora del primer uso
6. Si no existe:
   - Muestra: ⚠️ TICKET FALSO
   - Alerta de posible clonación

## 🧪 Testing

```powershell
# Ejecutar tests
python manage.py test

# Con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Panel de Administración

Acceder a: http://localhost:8000/admin/

Funcionalidades:
- Gestión completa de usuarios, eventos, zonas
- Visualización de ventas y tickets
- No permite eliminar validaciones (auditoría)
- No permite crear validaciones manualmente (solo por API)

## 🔧 Desarrollo

### Crear nuevas migraciones
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Cargar datos de ejemplo
```powershell
python manage.py loaddata fixtures/datos_ejemplo.json
```

### Shell interactivo
```powershell
python manage.py shell
```

## 📦 Dependencias Principales

- **Django 5.0.2**: Framework web
- **djangorestframework 3.14.0**: API REST
- **django-cors-headers**: CORS para frontend
- **Pillow**: Procesamiento de imágenes
- **qrcode**: Generación de códigos QR
- **python-dotenv**: Variables de entorno
- **drf-yasg**: Documentación Swagger

## 🚀 Despliegue

Para producción:
1. Cambiar `DEBUG=False` en `.env`
2. Configurar base de datos PostgreSQL
3. Configurar `ALLOWED_HOSTS`
4. Recolectar archivos estáticos: `python manage.py collectstatic`
5. Usar servidor WSGI (Gunicorn, uWSGI)

## 👥 Roles de Usuario

- **ADMIN**: Acceso total al sistema
- **VENDEDOR**: Puede crear ventas y ver sus propias ventas
- **VALIDADOR**: Puede validar tickets en la puerta

## 📝 Licencia

Sistema propietario - Todos los derechos reservados.
