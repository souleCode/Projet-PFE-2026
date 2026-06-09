from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-changeme-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # Désactivé en dev pour permettre à runserver de servir staticfiles
  
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'storages',
    # Apps
    'Apps.Users',
    'Apps.Cameras',
    'Apps.detection',
    'Apps.alertes',
    'Apps.audits',
    'Apps.RegleSHE',
    ## extensions
    'django_extensions',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Sert les fichiers statiques en prod avec WhiteNoise
]

ROOT_URLCONF = 'api.urls'

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

DB_NAME = config('DB_NAME', default='')
DB_USER = config('DB_USER', default='')
DB_PASSWORD = config('DB_PASSWORD', default='')
DB_HOST = config('DB_HOST', default='')
DB_PORT = config('DB_PORT', default='5432')
DB_SSLMODE = config('DB_SSLMODE', default='require')

USE_POSTGRES = config('USE_POSTGRES', default=True, cast=bool)

if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "CONN_MAX_AGE": 60,
            "OPTIONS": {
                "sslmode": DB_SSLMODE,
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / 'db.sqlite3',
            "OPTIONS": {
                "timeout": 20,
            },
        }
    }

AUTH_USER_MODEL = 'Users.User'

# ====================== DRF : authentification via cookie ===========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'Apps.Users.Authentication.CookieJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Nombre d'alertes par page par défaut (modifiable via ?page_size=...)
}

# ================== JWT============================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ======================== Noms des cookies ==========================
JWT_AUTH_COOKIE         = 'access_token'   # cookie access
JWT_AUTH_REFRESH_COOKIE = 'refresh_token'  # cookie refresh
JWT_AUTH_COOKIE_SECURE  = not DEBUG        # True en prod (HTTPS)
JWT_AUTH_COOKIE_HTTPONLY = True            # Pas accessible en JS
JWT_AUTH_COOKIE_SAMESITE = config(
    'JWT_AUTH_COOKIE_SAMESITE',
    default='Lax' if DEBUG else 'None',
)

# =====================CORS ==============================
CORS_DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:3000",
    "https://epi-preprod.digiscia.me",
    "https://pfe-api.digiscia.me",
]
EXTRA_CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config('EXTRA_CORS_ALLOWED_ORIGINS', default='').split(',')
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True   # Obligatoire pour envoyer les cookies
CORS_ALLOWED_ORIGINS = list(dict.fromkeys(CORS_DEFAULT_ORIGINS + EXTRA_CORS_ALLOWED_ORIGINS))

# ======================= CSRF =======================
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CORS_DEFAULT_ORIGINS + EXTRA_CORS_ALLOWED_ORIGINS))
CSRF_COOKIE_NAME     = 'csrftoken'
CSRF_COOKIE_HTTPONLY = False   # Le frontend doit pouvoir lire le csrftoken
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = config(
    'CSRF_COOKIE_SAMESITE',
    default='Lax' if DEBUG else 'None',
)
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = config(
    'SESSION_COOKIE_SAMESITE',
    default='Lax' if DEBUG else 'None',
)

# ================== Media / Static ======================
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Europe/Paris'
USE_I18N = True
USE_TZ   = True

YOLO_MODEL_PATH = BASE_DIR / 'models' / 'best.pt'

GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
GEMINI_MODEL = config('GEMINI_MODEL', default='gemini-2.5-flash')
GEMINI_PERSISTENCE_MINUTES = config('GEMINI_PERSISTENCE_MINUTES', default=0.1, cast=float)
GEMINI_DAILY_LIMIT = config('GEMINI_DAILY_LIMIT', default=5, cast=int)



AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-north-1')
AWS_S3_ENDPOINT_URL = f'https://s3.{AWS_S3_REGION_NAME}.amazonaws.com'
AWS_S3_ADDRESSING_STYLE = 'path'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = config('AWS_QUERYSTRING_AUTH', default=True, cast=bool)

USE_S3 = bool(AWS_STORAGE_BUCKET_NAME and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)

if USE_S3:
    STORAGES = {
        'default': {
            'BACKEND': 'api.storage_backends.MediaStorage',
        },
        'staticfiles': {
            'BACKEND': 'api.storage_backends.StaticStorage',
        },
    }
    if not AWS_QUERYSTRING_AUTH:
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'