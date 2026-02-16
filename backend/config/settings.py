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
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Claves de encriptación para tickets (AES-256 + HMAC)
# IMPORTANTE: Mantener estas claves secretas y no compartir
# Las claves por defecto son SOLO para desarrollo/pruebas
# En producción, genera claves únicas con: python -c "import secrets; print(secrets.token_hex(32))"
TICKET_ENCRYPTION_KEY = os.getenv(
    'TICKET_ENCRYPTION_KEY',
    'a1b2c3d4e5f61234567890abcdef0123456789abcdef0123456789abcdef0123'  # DEFAULT: 64 chars hex (32 bytes)
)
TICKET_HMAC_KEY = os.getenv(
    'TICKET_HMAC_KEY', 
    'f2e1d0c9b8a76543210fedcba9876543210fedcba9876543210fedcba98765'  # DEFAULT: 64 chars hex (32 bytes)
)

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
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Session Configuration
SESSION_COOKIE_SAMESITE = 'Lax'  # Permite cookies en solicitudes cross-origin básicas
SESSION_COOKIE_SECURE = False  # True solo en producción con HTTPS
SESSION_COOKIE_HTTPONLY = True  # Previene acceso JavaScript a la cookie
SESSION_COOKIE_AGE = 86400  # 24 horas (en segundos)
SESSION_SAVE_EVERY_REQUEST = True  # Renueva la sesión en cada petición
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # La sesión persiste al cerrar el navegador

# CSRF Configuration
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False  # True solo en producción con HTTPS
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# QR Code Configuration
QR_CODE_DIR = 'qr_codes'
QR_CODE_PATH = MEDIA_ROOT / QR_CODE_DIR
