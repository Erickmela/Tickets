"""
Django settings for Jala Jala Tickets System project.
Aplicando principios SOLID y configuración modular.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Configurar BASE_DIR primero
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar .env desde la raíz del proyecto backend
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,*').split(',')

# Claves de encriptación para tickets (AES-256 + HMAC)
# IMPORTANTE: Mantener estas claves secretas y no compartir
# Deben estar definidas en el archivo .env
# Para generar nuevas claves: python -c "import secrets; print(secrets.token_hex(32))"
TICKET_ENCRYPTION_KEY = os.getenv('TICKET_ENCRYPTION_KEY')
TICKET_HMAC_KEY = os.getenv('TICKET_HMAC_KEY')

# Validar que las claves estén configuradas
if not TICKET_ENCRYPTION_KEY or not TICKET_HMAC_KEY:
    raise ValueError('TICKET_ENCRYPTION_KEY y TICKET_HMAC_KEY deben estar definidas en el archivo .env')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    
    # Local apps
    'apps.usuarios',
    'apps.eventos',
    'apps.ventas',
    'apps.validaciones',
    'apps.reportes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Usar PostgreSQL si está configurado en .env, sino SQLite
db_engine = os.getenv('DATABASE_ENGINE') or os.getenv('DB_ENGINE')
if db_engine:
    DATABASES = {
        'default': {
            'ENGINE': db_engine,
            'NAME': os.getenv('DATABASE_NAME') or os.getenv('DB_NAME'),
            'USER': os.getenv('DATABASE_USER') or os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD') or os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST') or os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DATABASE_PORT') or os.getenv('DB_PORT', '5432'),
        }
    }
else:
    # SQLite como fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'usuarios.Usuario'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'config.authentication.CsrfExemptSessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'config.pagination.CustomPageNumberPagination',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # Throttling para proteger el servidor de sobrecarga
    'DEFAULT_THROTTLE_CLASSES': [
        'config.throttling.ClienteRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'cliente': '300/hour',   # 300 peticiones por hora para clientes (5 por minuto)
        'compra': '30/hour',     # 30 compras por hora por cliente (suficiente para uso normal)
        'anon': '100/hour',      # 100 peticiones por hora para anónimos
    }
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# Session Configuration
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF Configuration
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# QR Code Configuration
QR_CODE_DIR = 'qr_codes'
QR_CODE_PATH = MEDIA_ROOT / QR_CODE_DIR

# Redis Configuration (Cola Virtual)
# En desarrollo: Redis local
# En producción: Usar REDIS_URL del proveedor (Upstash, Redis Cloud, etc.)
REDIS_URL = os.getenv('REDIS_URL')  # Ejemplo: redis://default:password@host:port
if REDIS_URL:
    # Producción - Parsear URL completa
    import urllib.parse as urlparse
    url = urlparse.urlparse(REDIS_URL)
    REDIS_HOST = url.hostname
    REDIS_PORT = url.port or 6379
    REDIS_PASSWORD = url.password
    REDIS_DB = 0
else:
    # Desarrollo - Redis local
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

# MercadoPago Configuration
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_PUBLIC_KEY = os.getenv('MERCADOPAGO_PUBLIC_KEY')
MERCADOPAGO_WEBHOOK_SECRET = os.getenv('MERCADOPAGO_WEBHOOK_SECRET')
MERCADOPAGO_STATEMENT_DESCRIPTOR = os.getenv('MERCADOPAGO_STATEMENT_DESCRIPTOR', 'TICKETS')

# URLs para callbacks de MercadoPago
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
