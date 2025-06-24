
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url # Importado para configurar la base de datos desde la URL

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# La SECRET_KEY se leerá desde las variables de entorno de Render
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG se deshabilita en producción, a menos que se especifique en las variables de entorno
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS se configura para aceptar la URL de tu servicio en Render
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(' ')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Añadido para servir archivos estáticos
    'django.contrib.staticfiles',
    # Third-party apps
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    # Mis Apps
    'apps.users',
    'apps.academic_setup',
    'apps.scheduling',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Añadido para servir archivos estáticos
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'la_pontificia_horarios.urls'

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

WSGI_APPLICATION = 'la_pontificia_horarios.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Se usa dj-database-url para leer la variable DATABASE_URL de Render
# El ssl_require=True es crucial para las conexiones a bases de datos de Render.
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# CELERY SETTINGS
# Para producción, esto debería apuntar a un servicio de Redis o RabbitMQ en la nube,
# configurado también a través de variables de entorno.
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'rpc://')


# Internationalization
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
# Directorio donde `collectstatic` reunirá todos los archivos estáticos para producción.
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Configuración para que WhiteNoise sirva los archivos estáticos de forma eficiente.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SIGNING_KEY': SECRET_KEY, # Ya está usando la SECRET_KEY de las variables de entorno
    'AUTH_HEADER_TYPES': ('Bearer',),
    # ... resto de la configuración de SIMPLE_JWT ...
}


# CORS Settings
# Se leerá la URL del frontend desde una variable de entorno
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:8080')
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
CORS_ALLOW_CREDENTIALS = True

# Añadir el host de Render a ALLOWED_HOSTS si está disponible
RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)
