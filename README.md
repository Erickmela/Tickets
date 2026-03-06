# Sistema de Tickets Jala Jala

Sistema completo de gestión y venta de tickets para eventos con seguridad avanzada, integración de pagos y control de acceso en tiempo real.

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Seguridad de Tickets](#seguridad-de-tickets)
4. [Sistema de Cola Virtual](#sistema-de-cola-virtual)
5. [Integración de MercadoPago](#integración-de-mercadopago)
6. [Roles y Permisos](#roles-y-permisos)
7. [Instalación y Configuración](#instalación-y-configuración)
8. [Variables de Entorno](#variables-de-entorno)
9. [Estructura del Proyecto](#estructura-del-proyecto)
10. [API Endpoints](#api-endpoints)
11. [Flujos de Operación](#flujos-de-operación)

---

## Descripción General

Sistema web diseñado para la gestión completa del ciclo de vida de tickets para eventos, desde la creación hasta la validación en puerta. Incluye protección contra fraudes, sistema de pagos integrado y optimización para alta concurrencia.

### Características Principales

- Gestión de eventos con múltiples presentaciones y zonas
- Venta de tickets online con integración de pagos
- Códigos QR únicos con encriptación AES-256
- Sistema de cola virtual para eventos de alta demanda
- Validación de tickets en tiempo real
- Panel administrativo completo
- Reportes y estadísticas

### Tecnologías

**Backend:**
- Python 3.x
- Django 5.0.2
- Django REST Framework 3.14.0
- PostgreSQL / SQLite
- Redis (cola virtual)

**Frontend:**
- Vue.js 3.4.15
- Vue Router 4.2.5
- Pinia 2.1.7 (gestión de estado)
- Tailwind CSS 3.4.1
- Axios 1.6.5
- Vite 5.0.11

**Servicios Externos:**
- MercadoPago SDK 2.2.1 (pagos)
- Redis (gestión de colas)

---

## Arquitectura del Sistema

El sistema sigue una arquitectura de tres capas con principios SOLID:

### Capa de Presentación (Frontend)
- Aplicación SPA con Vue.js 3
- Gestión de estado reactivo con Pinia
- Rutas protegidas según rol de usuario
- Componentes reutilizables con Composition API

### Capa de Lógica de Negocio (Backend)
- API RESTful con Django REST Framework
- Servicios de negocio separados por dominio
- Autenticación basada en sesiones
- Rate limiting para protección contra sobrecarga

### Capa de Datos
- Base de datos relacional (PostgreSQL en producción, SQLite en desarrollo)
- Redis para gestión de colas y cache
- Sistema de archivos para QR codes y media

### Principios SOLID Aplicados

- Single Responsibility: Cada modelo, servicio y vista tiene una única responsabilidad
- Open/Closed: Uso de enumeraciones y clases abstractas para extensibilidad
- Liskov Substitution: Interfaces consistentes en toda la aplicación
- Interface Segregation: APIs y serializers específicos por caso de uso
- Dependency Inversion: Servicios de negocio independientes de la capa de datos

---

## Seguridad de Tickets

El sistema implementa múltiples capas de seguridad para prevenir falsificación y clonación de tickets.

### Características de Seguridad

**1. UUID Único**
Cada ticket genera un UUID4 (128 bits) imposible de adivinar o predecir. Este identificador es único globalmente y no puede duplicarse.

**2. Encriptación AES-256**
El UUID del ticket se encripta usando AES-256-CBC (estándar militar) antes de incluirse en el código QR. Características:
- Clave de encriptación de 256 bits
- Vector de inicialización (IV) aleatorio por cada ticket
- Previene que el UUID sea visible en texto plano

**3. Firma HMAC-SHA256**
Cada código QR incluye una firma HMAC-SHA256 que garantiza:
- Integridad: Detecta cualquier modificación del código QR
- Autenticidad: Solo el sistema con las claves secretas puede generar QR válidos
- No repudio: Verifica que el token sea original del sistema

**4. Expiración Temporal**
Los tokens incluyen timestamp de emisión y expiración:
- Fecha de emisión encriptada en el token
- Fecha de expiración configurable (por defecto 1 año)
- Validación automática de vigencia

**5. Anti-Replay**
Sistema de verificación contra reutilización:
- Token encriptado almacenado en base de datos
- Validación exacta del token presentado vs token almacenado
- Detección de tickets clonados mediante comparación de tokens

**6. Validación de Uso Único**
- Registro de cada validación con timestamp y usuario validador
- Estado del ticket: NO_USADO, USADO, ANULADO
- Imposibilidad de reutilizar un ticket ya validado
- Historial completo de intentos de validación

### Flujo de Seguridad

```
Creación del Ticket:
1. Generar UUID4 único
2. Crear token con: UUID + timestamp + expiración
3. Encriptar token con AES-256 + IV aleatorio
4. Generar firma HMAC del token encriptado
5. Combinar: token_encriptado + firma
6. Generar código QR con el resultado
7. Almacenar token encriptado en BD

Validación del Ticket:
1. Escanear código QR
2. Extraer token encriptado + firma
3. Verificar firma HMAC (detecta manipulación)
4. Desencriptar token
5. Verificar expiración temporal
6. Buscar ticket por UUID en BD
7. Comparar token presentado vs token almacenado
8. Verificar estado NO_USADO
9. Marcar como USADO con timestamp
10. Registrar validación (usuario, hora, puerta)
```

### Configuración de Claves

Las claves de encriptación NUNCA deben exponerse. Deben configurarse en variables de entorno:

```
TICKET_ENCRYPTION_KEY: Clave AES-256 (64 caracteres hexadecimales)
TICKET_HMAC_KEY: Clave HMAC-SHA256 (64 caracteres hexadecimales)
```

Para generar claves seguras:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**IMPORTANTE:**
- Usar claves diferentes en desarrollo y producción
- Nunca incluir claves en el código fuente
- Nunca subir claves a repositorios Git
- Si se pierden las claves, los QR antiguos no podrán validarse
- Rotar claves periódicamente en producción

---

## Sistema de Cola Virtual

Sistema inteligente de gestión de tráfico para proteger el servidor durante eventos de alta demanda.

### Problema que Resuelve

Cuando miles de usuarios intentan comprar tickets simultáneamente (ej: conciertos populares), el servidor puede saturarse y caerse. Esto afecta negativamente a:
- Usuarios intentando comprar (experiencia frustrante)
- Personal validando tickets en otras presentaciones (interrupciones)
- Estabilidad general del sistema

### Solución: Cola Virtual con Redis

El sistema implementa una sala de espera virtual que:
- Limita usuarios comprando simultáneamente a un número seguro (configurable, por defecto 300)
- Coloca usuarios adicionales en una cola ordenada (primero en llegar, primero en comprar)
- Muestra posición en la cola y tiempo estimado de espera
- Procesa la cola automáticamente cuando hay espacio disponible
- Bypass automático para personal del sistema (ADMIN, VALIDADOR, VENDEDOR)

### Arquitectura de la Cola

**Backend: VirtualQueueService (queue_service.py)**

Servicio Python que gestiona:
- join_queue(): Agregar usuario a la cola con timestamp
- activate_user(): Mover usuario de cola a activos
- is_user_active(): Verificar si usuario puede comprar
- get_queue_position(): Obtener posición actual en cola
- process_queue(): Activar automáticamente siguientes usuarios
- bypass_queue_for_staff(): Permitir acceso directo a personal
- deactivate_user(): Remover usuario al completar/abandonar compra
- clear_queue(): Limpiar cola (administración)
- get_queue_stats(): Estadísticas para monitoreo

**Estructuras de Datos en Redis:**

1. Sorted Set (cola de espera):
   - Key: `queue:evento:{slug}:waiting`
   - Score: timestamp Unix
   - Member: user_id o session_id
   - Ordenamiento automático por tiempo de llegada

2. Set (usuarios activos):
   - Key: `queue:evento:{slug}:active_users`
   - Members: usuarios con permiso de compra
   - TTL automático (timeout de sesión)

**API Endpoints:**

```
POST   /api/ventas/ventas/check-queue/
       Body: { "evento_slug": "nombre-evento" }
       Response: { "status": "active" } o { "status": "waiting", "position": 45 }

GET    /api/ventas/ventas/queue-position/?evento_slug=nombre-evento
       Response: { "position": 45, "total_in_queue": 150, "estimated_wait": 90 }

POST   /api/ventas/ventas/leave-queue/
       Body: { "evento_slug": "nombre-evento" }
       Response: { "success": true }

GET    /api/ventas/ventas/queue-stats/?evento_slug=nombre-evento
       Response: { "active": 300, "waiting": 150, "total": 450 }
       Permisos: Solo ADMIN
```

**Frontend: VirtualQueue.vue**

Componente de sala de espera que muestra:
- Spinner animado
- Posición actual en la cola (ej: "Posición 45 de 150")
- Tiempo estimado de espera (ej: "1m 30s")
- Barra de progreso visual
- Botón para cancelar y salir
- Actualización automática cada 3 segundos

Eventos emitidos:
- `active`: Usuario puede proceder a comprar
- `cancelled`: Usuario canceló la espera

### Configuración del Sistema

**Variables en queue_service.py:**

```python
MAX_CONCURRENT_USERS = 300     # Usuarios comprando simultáneamente
QUEUE_TIMEOUT = 900            # Tiempo máximo en cola (15 minutos)
ACTIVE_SESSION_TIMEOUT = 600   # Tiempo para completar compra (10 minutos)
```

**Ajustar según capacidad del servidor:**
- Servidor potente: MAX_CONCURRENT_USERS = 500
- Servidor moderado: MAX_CONCURRENT_USERS = 300
- Servidor básico: MAX_CONCURRENT_USERS = 150

### Flujo de Operación

```
Escenario 1: Baja Demanda (< 300 usuarios comprando)
Usuario -> Click "Comprar" -> Compra directa SIN cola

Escenario 2: Alta Demanda (300+ usuarios comprando)
Usuario -> Click "Comprar" -> 
  Verificar demanda ->
  Agregar a cola ->
  Mostrar sala de espera ->
  Polling cada 3 segundos ->
  Esperar turno ->
  Activación automática ->
  Proceder a compra

Escenario 3: Usuario Staff (ADMIN/VALIDADOR/VENDEDOR)
Usuario Staff -> Click "Comprar" -> Bypass automático -> Compra directa
```

### Instalación y Configuración

**1. Instalar Redis:**

Windows (Chocolatey):
```powershell
choco install redis-64
```

Windows (Manual):
- Descargar: https://github.com/tporadowski/redis/releases
- Extraer y ejecutar redis-server.exe

Linux:
```bash
sudo apt-get install redis-server
```

**2. Instalar dependencia Python:**
```bash
pip install redis
```

**3. Configurar variables de entorno:**

Desarrollo (Redis local):
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

Producción (Upstash/Redis Cloud):
```
REDIS_URL=redis://default:password@host:port
```

**4. Verificar instalación:**
```bash
redis-cli ping
# Debe responder: PONG
```

### Costos de Redis en Producción

**Opciones gratuitas:**

1. Upstash (Recomendado)
   - Plan gratuito: 10,000 comandos/día
   - Suficiente para ~500 usuarios/día con cola
   - URL: https://upstash.com

2. Redis Cloud
   - Plan gratuito: 30MB (~10,000 usuarios en cola)
   - URL: https://redis.com

3. Render
   - Plan gratuito: 25MB
   - URL: https://render.com

**Planes pagos (si creces mucho):**
- Upstash: $0.20 por 100k comandos (~$6/mes para 1,500 usuarios/día)
- Redis Cloud/Render: $7/mes (100MB)

**Conclusión:** Puedes empezar gratis y solo pagar cuando tengas tráfico alto.

### Graceful Degradation

Si Redis no está disponible:
- Sistema funciona normalmente SIN cola virtual
- No se producen errores ni bloqueos
- Log: "Redis no disponible. Cola virtual desactivada."
- Todos los usuarios acceden directamente

---

## Integración de MercadoPago

Sistema completo de pagos online con MercadoPago Checkout Pro.

### Características

- Creación de preferencias de pago
- Integración con SDK de MercadoPago v2
- Webhooks para notificaciones automáticas
- Validación HMAC-SHA256 de webhooks
- Creación automática de ventas al aprobar pago
- Gestión de estados de pago
- Reconciliación de carrito
- Interfaz de usuario para selección de método de pago
- Vista de resultado de pago con verificación

### Componentes Backend

**Servicios:**

1. **payment_status_mapper.py**
   - Mapea estados de MercadoPago a estados internos
   - Estados: PENDIENTE, APROBADO, RECHAZADO, CANCELADO, etc.

2. **webhook_validation_service.py**
   - Valida firma HMAC de webhooks de MercadoPago
   - Previene webhooks fraudulentos
   - Verifica integridad de notificaciones

3. **order_creation_service.py**
   - Crea órdenes de pago en el sistema
   - Vincula pago con carrito de usuario
   - Genera referencia única

4. **cart_reconciliation_service.py**
   - Reconcilia items del carrito con el pago
   - Verifica disponibilidad de tickets
   - Crea tickets al aprobar pago

5. **mercadopago_webhook_service.py**
   - Orquestador principal de webhooks
   - Procesa notificaciones de MercadoPago
   - Actualiza estado de órdenes
   - Crea ventas automáticamente

**API Endpoints:**

```
POST   /api/ventas/mercadopago/create_preference/
       Body: { "items": [...], "back_urls": {...} }
       Response: { "preference_id": "xxx", "init_point": "https://..." }

POST   /api/ventas/mercadopago/webhook_notification/
       Headers: x-signature, x-request-id
       Body: { "data": { "id": "payment_id" } }
       Response: { "status": "ok" }

GET    /api/ventas/mercadopago/payment_status/?payment_id=xxx
       Response: { "status": "approved", "orden": {...} }
```

### Componentes Frontend

**Servicios:**

1. **mercadopagoService.js**
   - Comunicación con API de backend
   - createPreference(): Crear preferencia de pago
   - getPaymentStatus(): Consultar estado de pago
   - Manejo de errores

**Componentes:**

1. **Checkout.vue (modificado)**
   - Botón de MercadoPago integrado
   - Carga SDK automáticamente
   - Inicializa preferencia
   - Redirige a MercadoPago

2. **PagoResultado.vue**
   - Vista de resultado de pago
   - Verificación de estado
   - Limpieza de carrito
   - Mensajes según resultado

### Flujo de Pago Completo

```
1. Usuario agrega tickets al carrito
2. Usuario hace click en "Pagar"
3. Frontend selecciona método de pago (MercadoPago)
4. Frontend solicita crear preferencia (POST create_preference)
5. Backend crea preferencia en MercadoPago
6. Backend retorna preference_id
7. Frontend inicializa SDK con preference_id
8. Usuario es redirigido a MercadoPago
9. Usuario completa el pago en MercadoPago
10. MercadoPago envía webhook a backend
11. Backend valida webhook (HMAC)
12. Backend consulta estado del pago
13. Si aprobado: Backend crea venta y tickets
14. Usuario es redirigido a PagoResultado
15. Frontend consulta estado final
16. Frontend muestra resultado y limpia carrito
```

### Configuración

**Backend (settings.py):**
```python
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_PUBLIC_KEY = os.getenv('MERCADOPAGO_PUBLIC_KEY')
MERCADOPAGO_WEBHOOK_SECRET = os.getenv('MERCADOPAGO_WEBHOOK_SECRET')
```

**Frontend (.env):**
```
VITE_MERCADOPAGO_PUBLIC_KEY=TEST-xxx-public-key
```

### Obtener Credenciales

1. Crear cuenta en MercadoPago: https://www.mercadopago.com
2. Ir a: https://www.mercadopago.com/developers/panel/app
3. Crear aplicación
4. Copiar:
   - Access Token (backend)
   - Public Key (frontend)
   - Webhook Secret (backend)

**Credenciales de Prueba:**
- TEST-xxx: Para desarrollo
- APP-xxx: Para producción

**IMPORTANTE:**
- Nunca compartir Access Token
- No incluir credenciales en código fuente
- Usar credenciales TEST en desarrollo
- Usar credenciales APP en producción

### Tarjetas de Prueba

Para probar pagos en desarrollo:

```
Tarjeta Aprobada:
Número: 5031 7557 3453 0604
CVV: 123
Fecha: 11/25

Tarjeta Rechazada:
Número: 5031 4332 1540 6351
CVV: 123
Fecha: 11/25
```

Más tarjetas: https://www.mercadopago.com.pe/developers/es/docs/checkout-pro/additional-content/test-cards

---

## Roles y Permisos

El sistema implementa control de acceso basado en roles (RBAC).

### Roles Disponibles

**1. CLIENTE**
- Usuario público del sistema
- Puede: Comprar tickets, ver eventos, gestionar perfil
- No puede: Acceder a panel administrativo, validar tickets

**2. VALIDADOR**
- Personal de puerta en eventos
- Puede: Escanear y validar tickets, ver evento asignado
- No puede: Crear eventos, ver reportes financieros, gestionar usuarios

**3. VENDEDOR**
- Personal de venta en punto físico
- Puede: Crear ventas manuales, buscar clientes, generar tickets
- No puede: Validar tickets, ver reportes completos

**4. ADMIN**
- Administrador del sistema
- Puede: Todo (crear eventos, ver reportes, gestionar usuarios, configurar sistema)
- Acceso completo sin restricciones

### Permisos por Módulo

**Eventos:**
- Ver lista: Todos (público)
- Ver detalle: Todos (público)
- Crear/Editar/Eliminar: Solo ADMIN

**Tickets:**
- Comprar: CLIENTE (online), VENDEDOR (punto físico)
- Ver propios: CLIENTE
- Validar: VALIDADOR
- Ver todos: ADMIN

**Ventas:**
- Crear: CLIENTE (auto), VENDEDOR (manual), ADMIN
- Ver propias: CLIENTE
- Ver todas: ADMIN

**Validaciones:**
- Crear: VALIDADOR, ADMIN
- Ver del evento: VALIDADOR (solo su evento), ADMIN (todos)
- Ver todas: ADMIN

**Reportes:**
- Ver básicos: VENDEDOR (sus ventas)
- Ver completos: ADMIN

**Usuarios:**
- Crear: Público (registro como CLIENTE), ADMIN (cualquier rol)
- Editar propio: Todos
- Editar cualquiera: ADMIN
- Cambiar rol: Solo ADMIN

### Bypass de Restricciones

**Rate Limiting:**
ADMIN, VALIDADOR y VENDEDOR tienen bypass automático de rate limiting:
- No tienen límite de peticiones por hora
- No entran en la cola virtual
- Acceso prioritario al sistema

**Cola Virtual:**
Personal del sistema (ADMIN, VALIDADOR, VENDEDOR) nunca espera en cola:
- Bypass automático incluso en alta demanda
- Pueden trabajar sin interrupciones durante eventos populares

### Implementación de Permisos

**Backend (DRF):**
```python
from rest_framework.permissions import IsAuthenticated

class EventoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdmin()]
        return [AllowAny()]
```

**Frontend (Vue Router):**
```javascript
{
  path: '/admin',
  meta: { requiresAuth: true, allowedRoles: ['ADMIN'] }
}
```

---

## Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- Node.js 16 o superior
- PostgreSQL 13 o superior (producción) / SQLite (desarrollo)
- Redis 7.x (opcional, para cola virtual)

### Instalación Backend

**1. Clonar repositorio:**
```bash
git clone <repository-url>
cd Tickets/backend
```

**2. Crear entorno virtual:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

**3. Instalar dependencias:**
```bash
pip install -r requirements.txt
```

**4. Configurar variables de entorno:**
Copiar `.env.example` a `.env` y configurar:
```bash
cp .env.example .env
# Editar .env con tus valores
```

**5. Generar claves secretas:**
```bash
# SECRET_KEY de Django
python -c "import secrets; print(secrets.token_urlsafe(50))"

# TICKET_ENCRYPTION_KEY (64 caracteres hex)
python -c "import secrets; print(secrets.token_hex(32))"

# TICKET_HMAC_KEY (64 caracteres hex)
python -c "import secrets; print(secrets.token_hex(32))"
```

**6. Aplicar migraciones:**
```bash
python manage.py migrate
```

**7. Crear superusuario:**
```bash
python manage.py createsuperuser
```

**8. Iniciar servidor:**
```bash
python manage.py runserver
```

**9. Acceder:**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

### Instalación Frontend

**1. Navegar a directorio:**
```bash
cd ../frontend
```

**2. Instalar dependencias:**
```bash
npm install
```

**3. Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus valores
```

**4. Iniciar servidor de desarrollo:**
```bash
npm run dev
```

**5. Acceder:**
- http://localhost:5173

### Instalación Opcional: Redis (Cola Virtual)

**Windows (Chocolatey):**
```powershell
choco install redis-64
redis-server
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Verificar:**
```bash
redis-cli ping
# Debe responder: PONG
```

### Configuración de Base de Datos

**Desarrollo (SQLite):**
No requiere configuración adicional. Django crea `db.sqlite3` automáticamente.

**Producción (PostgreSQL):**

1. Crear base de datos:
```sql
CREATE DATABASE tickets_db;
CREATE USER tickets_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE tickets_db TO tickets_user;
```

2. Configurar en `.env`:
```
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=tickets_db
DATABASE_USER=tickets_user
DATABASE_PASSWORD=tu_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

---

## Variables de Entorno

### Backend (.env)

**Django Core:**
```
SECRET_KEY=tu-clave-secreta-django-50-caracteres-minimo
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com
```

**Base de Datos (Opcional - usa SQLite si no se configura):**
```
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=tickets_db
DATABASE_USER=tickets_user
DATABASE_PASSWORD=password_seguro
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**Seguridad de Tickets:**
```
TICKET_ENCRYPTION_KEY=clave-hex-64-caracteres-para-aes-256-encriptacion
TICKET_HMAC_KEY=clave-hex-64-caracteres-para-hmac-sha256-firma
```

**Redis (Cola Virtual - Opcional):**
```
# Desarrollo (Redis local)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# O Producción (URL completa)
REDIS_URL=redis://default:password@host.upstash.io:6379
```

**MercadoPago:**
```
MERCADOPAGO_ACCESS_TOKEN=TEST-xxx-tu-access-token-de-mercadopago
MERCADOPAGO_PUBLIC_KEY=TEST-xxx-tu-public-key-de-mercadopago
MERCADOPAGO_WEBHOOK_SECRET=tu-webhook-secret-key
MERCADOPAGO_STATEMENT_DESCRIPTOR=TICKETS
```

**CORS (Frontend URLs permitidas):**
```
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://tu-frontend.com
```

### Frontend (.env)

```
# URL del Backend API
VITE_API_URL=http://localhost:8000/api

# MercadoPago Public Key
VITE_MERCADOPAGO_PUBLIC_KEY=TEST-xxx-tu-public-key
```

**Notas:**
- Variables con prefijo `VITE_` están disponibles en el frontend
- Cambiar `http://localhost:8000` por tu URL de producción
- Usar credenciales TEST en desarrollo, APP en producción

---

## Estructura del Proyecto

```
Tickets/
├── backend/
│   ├── config/                      # Configuración Django
│   │   ├── settings.py             # Settings principal
│   │   ├── urls.py                 # URLs principales
│   │   ├── authentication.py       # Auth personalizada
│   │   ├── encryption.py           # Encriptación AES-256
│   │   ├── throttling.py           # Rate limiting
│   │   ├── pagination.py           # Paginación
│   │   └── hashid_utils.py         # Hashids para URLs
│   │
│   ├── apps/
│   │   ├── usuarios/               # Gestión de usuarios
│   │   │   ├── models.py          # Usuario, PerfilCliente
│   │   │   ├── serializers.py     # Serializers de usuario
│   │   │   ├── views.py           # ViewSets y auth
│   │   │   └── urls.py
│   │   │
│   │   ├── eventos/                # Gestión de eventos
│   │   │   ├── models.py          # Evento, Presentacion, Zona
│   │   │   ├── serializers/       # Serializers por caso de uso
│   │   │   ├── views/             # ViewSets separados
│   │   │   └── urls.py
│   │   │
│   │   ├── ventas/                 # Ventas y tickets
│   │   │   ├── models.py          # Venta, Orden, Ticket
│   │   │   ├── serializers/       # Serializers de venta
│   │   │   ├── views/             # ViewSets de venta
│   │   │   ├── services/          # Servicios de negocio
│   │   │   │   ├── queue_service.py           # Cola virtual
│   │   │   │   ├── mercadopago_webhook_service.py
│   │   │   │   └── ...
│   │   │   └── urls.py
│   │   │
│   │   ├── validaciones/           # Validación de tickets
│   │   │   ├── models.py          # Validacion
│   │   │   ├── serializers.py     # Serializers validación
│   │   │   ├── views.py           # API de escaneo
│   │   │   └── urls.py
│   │   │
│   │   └── reportes/               # Reportes y estadísticas
│   │       ├── services.py        # Lógica de reportes
│   │       ├── utils.py           # Generación PDF/Excel
│   │       ├── views.py           # APIs de reportes
│   │       └── urls.py
│   │
│   ├── media/                      # Archivos subidos
│   │   ├── eventos/               # Imágenes de eventos
│   │   └── qr_codes/              # Códigos QR generados
│   │
│   ├── requirements.txt           # Dependencias Python
│   ├── manage.py                  # CLI de Django
│   └── db.sqlite3                # BD desarrollo
│
├── frontend/
│   ├── src/
│   │   ├── components/            # Componentes Vue
│   │   │   ├── Queue/
│   │   │   │   └── VirtualQueue.vue
│   │   │   ├── Admin/
│   │   │   ├── Evento/
│   │   │   └── ...
│   │   │
│   │   ├── views/                 # Vistas principales
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── EventoDetalleView.vue
│   │   │   ├── CheckoutView.vue
│   │   │   ├── PagoResultado.vue
│   │   │   └── ...
│   │   │
│   │   ├── services/              # Servicios API
│   │   │   ├── api.js            # Cliente Axios
│   │   │   ├── authService.js    # Autenticación
│   │   │   ├── eventosService.js # Eventos
│   │   │   ├── ventasService.js  # Ventas y cola
│   │   │   ├── mercadopagoService.js
│   │   │   └── ...
│   │   │
│   │   ├── stores/                # Pinia stores
│   │   ├── router/                # Vue Router
│   │   ├── Helpers/               # Utilidades
│   │   ├── Layouts/               # Layouts
│   │   └── main.js               # Punto de entrada
│   │
│   ├── public/                    # Archivos estáticos
│   ├── package.json              # Dependencias npm
│   ├── vite.config.js            # Config Vite
│   └── tailwind.config.js        # Config Tailwind
│
└── README.md                      # Este archivo
```

---

## API Endpoints

### Autenticación

```
POST   /api/usuarios/login/
       Body: { "email": "user@example.com", "password": "password" }
       Response: { "usuario": {...}, "message": "Inicio de sesión exitoso" }

POST   /api/usuarios/logout/
       Response: { "message": "Sesión cerrada exitosamente" }

POST   /api/usuarios/register/
       Body: { "email": "...", "password": "...", "nombre": "...", ... }
       Response: { "id": 1, "email": "...", "rol": "CLIENTE" }

GET    /api/usuarios/me/
       Response: { "id": 1, "email": "...", "nombre": "...", "rol": "CLIENTE" }
```

### Eventos

```
GET    /api/eventos/eventos/
       Query: ?categoria=1&estado=PUBLICADO&search=concierto
       Response: { "count": 10, "results": [...] }

GET    /api/eventos/eventos/{slug}/
       Response: { "id": 1, "titulo": "...", "presentaciones": [...] }

GET    /api/eventos/categorias/
       Response: [{ "id": 1, "nombre": "Conciertos" }, ...]

GET    /api/eventos/presentaciones/
       Query: ?evento__slug=mi-evento
       Response: [{ "id": 1, "fecha": "2026-06-01", "zonas": [...] }]
```

### Ventas

```
POST   /api/ventas/ventas/
       Body: { "items": [{ "zona_id": 1, "cantidad": 2 }] }
       Response: { "id": 1, "total": 100.00, "tickets": [...] }

GET    /api/ventas/ventas/mis_ventas/
       Response: [{ "id": 1, "fecha": "...", "total": 100.00 }]

GET    /api/ventas/tickets/mis_tickets/
       Response: [{ "id": 1, "codigo": "...", "qr_code_url": "..." }]
```

### Cola Virtual

```
POST   /api/ventas/ventas/check-queue/
       Body: { "evento_slug": "mi-evento" }
       Response: { "status": "active" } | { "status": "waiting", "position": 45 }

GET    /api/ventas/ventas/queue-position/?evento_slug=mi-evento
       Response: { "position": 45, "total_in_queue": 150, "estimated_wait": 90 }

POST   /api/ventas/ventas/leave-queue/
       Body: { "evento_slug": "mi-evento" }

GET    /api/ventas/ventas/queue-stats/?evento_slug=mi-evento
       Response: { "active": 300, "waiting": 150, "total": 450 }
```

### MercadoPago

```
POST   /api/ventas/mercadopago/create_preference/
       Body: { "items": [...], "back_urls": {...} }
       Response: { "preference_id": "xxx", "init_point": "https://..." }

POST   /api/ventas/mercadopago/webhook_notification/
       Headers: x-signature, x-request-id
       Body: { "data": { "id": "payment_id" } }

GET    /api/ventas/mercadopago/payment_status/?payment_id=xxx
       Response: { "status": "approved", "orden": {...} }
```

### Validaciones

```
POST   /api/validaciones/validaciones/validar/
       Body: { "token_encriptado": "xxx" }
       Response: { "ticket": {...}, "validation": {...}, "status": "success" }

GET    /api/validaciones/validaciones/evento/{evento_id}/
       Response: [{ "ticket": {...}, "fecha": "...", "validador": {...} }]
```

### Reportes

```
GET    /api/reportes/dashboard/
       Response: { "ventas_hoy": 150, "ingresos_mes": 50000, ... }

GET    /api/reportes/ventas/?fecha_inicio=2026-01-01&fecha_fin=2026-12-31
       Response: { "total_ventas": 1000, "total_ingresos": 100000, ... }

GET    /api/reportes/evento/{evento_id}/pdf/
       Response: PDF file download

GET    /api/reportes/evento/{evento_id}/excel/
       Response: Excel file download
```

---

## Flujos de Operación

### Flujo de Compra de Ticket (Cliente)

```
1. Usuario navega a sitio web (no autenticado)
2. Ve lista de eventos disponibles
3. Click en evento para ver detalle
4. Selecciona presentación (fecha/hora)
5. Selecciona zona y cantidad de tickets
6. Agrega al carrito
7. Click en "Finalizar Compra"
8. Sistema solicita login/registro
9. Usuario inicia sesión o se registra
10. Sistema verifica cola virtual:
    - Si baja demanda: Continúa directo
    - Si alta demanda: Entra a sala de espera
11. Usuario en checkout
12. Selecciona método de pago:
    - Opción A: Efectivo (reserva, paga en punto físico)
    - Opción B: MercadoPago (pago online)
13. Si MercadoPago:
    a. Frontend crea preferencia
    b. Usuario redirigido a MercadoPago
    c. Completa pago
    d. MercadoPago envía webhook
    e. Sistema crea venta automáticamente
    f. Usuario redirigido a resultado
14. Si Efectivo:
    a. Sistema crea venta con estado PENDIENTE
    b. Genera código de reserva
15. Sistema genera tickets con QR único
16. Usuario recibe confirmación
17. Puede descargar tickets (PDF con QR)
18. Recibe email con tickets (opcional)
```

### Flujo de Validación de Ticket (Validador)

```
1. Validador inicia sesión en app móvil/web
2. Sistema verifica rol VALIDADOR
3. Validador accede a vista de escaneo
4. Sistema activa cámara
5. Validador escanea código QR del ticket
6. Frontend extrae token encriptado del QR
7. Frontend envía token a backend (POST /validar/)
8. Backend procesa validación:
   a. Verifica firma HMAC (autenticidad)
   b. Desencripta token con AES-256
   c. Extrae UUID del ticket
   d. Busca ticket en base de datos
   e. Compara token presentado vs almacenado
   f. Verifica estado NO_USADO
   g. Verifica que evento/zona correspondan
   h. Verifica que presentación sea hoy
9. Si validación exitosa:
   a. Marca ticket como USADO
   b. Registra validación (validador, timestamp, puerta)
   c. Retorna datos del ticket
   d. Frontend muestra ACCESO PERMITIDO (verde)
   e. Muestra datos: nombre, zona, asiento
10. Si validación fallida:
    a. Frontend muestra ACCESO DENEGADO (rojo)
    b. Muestra razón: ya usado, ticket inválido, clonado, etc.
11. Validador permite/deniega entrada
```

### Flujo de Creación de Venta Manual (Vendedor)

```
1. Vendedor inicia sesión en panel
2. Sistema verifica rol VENDEDOR
3. Vendedor accede a "Nueva Venta"
4. Busca o crea cliente
5. Selecciona evento/presentación
6. Selecciona zonas y cantidades
7. Sistema calcula total
8. Vendedor selecciona método de pago
9. Vendedor confirma datos
10. Sistema valida stock disponible
11. Sistema crea venta
12. Sistema genera tickets con QR
13. Vendedor imprime tickets
14. Entrega tickets al cliente
15. Cliente tiene tickets físicos con QR
```

### Flujo de Reportes (Admin)

```
1. Admin inicia sesión
2. Accede a sección "Reportes"
3. Selecciona tipo de reporte:
   - Dashboard general
   - Ventas por período
   - Ventas por evento
   - Validaciones por evento
   - Tickets vendidos vs validados
4. Aplica filtros:
   - Fecha inicio/fin
   - Evento específico
   - Zona específica
   - Método de pago
5. Sistema genera reporte
6. Admin visualiza datos:
   - Tablas
   - Gráficos
   - Estadísticas
7. Admin puede exportar:
   - PDF (impresión)
   - Excel (análisis)
8. Admin descarga archivo
```

---

## Documentación Adicional

Para más información detallada sobre componentes específicos:

- **SEGURIDAD_TICKETS.md**: Detalles técnicos de encriptación
- **COLA_VIRTUAL_SETUP.md**: Guía completa de cola virtual
- **COLA_VIRTUAL_RESUMEN.md**: Resumen ejecutivo de cola
- **OPTIMIZACIONES_RENDIMIENTO.md**: Rate limiting y optimización de queries
- **INTEGRACION_MERCADOPAGO_COMPLETA.md**: Integración completa de pagos

---

## Notas Finales

**Seguridad:**
- Nunca compartir claves secretas (TICKET_ENCRYPTION_KEY, TICKET_HMAC_KEY, SECRET_KEY)
- Nunca incluir credenciales en repositorio Git
- Usar HTTPS en producción
- Rotar claves periódicamente
- Mantener dependencias actualizadas

**Performance:**
- Redis opcional pero recomendado para eventos grandes
- PostgreSQL recomendado para producción
- Configurar MAX_CONCURRENT_USERS según capacidad del servidor
- Monitorear uso de Redis con get_queue_stats

**Mantenimiento:**
- Backup regular de base de datos
- Backup de claves de encriptación (sin ellas, QR antiguos no se pueden leer)
- Limpiar QR codes antiguos periódicamente
- Revisar logs de validaciones fallidas
- Monitorear webhooks de MercadoPago

**Soporte:**
- Django: https://docs.djangoproject.com
- Vue.js: https://vuejs.org
- MercadoPago: https://www.mercadopago.com/developers
- Redis: https://redis.io/docs
