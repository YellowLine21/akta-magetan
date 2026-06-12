"""
Django settings for akta_magetan project.
"""

from pathlib import Path
import os
import warnings
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a(&6p7bww8ccz1bqilrko3c3=!6!yfp15e^ld(fir7g*yr^j2)')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'permohonan',
    'admin_panel',
    'anymail',
]

AUTH_USER_MODEL = 'accounts.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'akta_magetan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'akta_magetan.wsgi.application'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Database - PostgreSQL via Railway (fallback ke SQLite untuk development lokal)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
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

# ── CSRF & SECURITY untuk Railway (HTTPS) ─────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://akta-magetan-skripsikeabsahanakta.up.railway.app',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

CSRF_COOKIE_SECURE    = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST  = True

# Internationalization
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── Email ──────────────────────────────────────────────────────
# Wajib diisi via environment variable di Railway.
# Jangan hardcode credentials di sini.
# ── Email via Resend (API, bukan SMTP) ────────────────────────
EMAIL_BACKEND = 'anymail.backends.resend.EmailBackend'

ANYMAIL = {
    'RESEND_API_KEY': os.environ.get('RESEND_API_KEY', ''),
}

DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'Dinas Kependudukan <onboarding@resend.dev>',  # ganti setelah verifikasi domain
)

if not os.environ.get('RESEND_API_KEY'):
    warnings.warn(
        "[akta_magetan] RESEND_API_KEY belum diset. Email tidak akan terkirim.",
        RuntimeWarning,
        stacklevel=2,
    )

EMAIL_HOST         = 'smtp.gmail.com'
EMAIL_PORT         = 465
EMAIL_USE_TLS      = False
EMAIL_USE_SSL      = True
EMAIL_HOST_USER    = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'Dinas Kependudukan dan Pencatatan Sipil Kabupaten Magetan',
)

# Peringatan startup jika env var email belum dikonfigurasi
if not EMAIL_HOST_USER:
    warnings.warn(
        "[akta_magetan] EMAIL_HOST_USER belum diset. "
        "Fitur pengiriman email tidak akan berfungsi. "
        "Set environment variable EMAIL_HOST_USER di Railway.",
        RuntimeWarning,
        stacklevel=2,
    )

if not EMAIL_HOST_PASSWORD:
    warnings.warn(
        "[akta_magetan] EMAIL_HOST_PASSWORD belum diset. "
        "Fitur pengiriman email tidak akan berfungsi. "
        "Set environment variable EMAIL_HOST_PASSWORD di Railway.",
        RuntimeWarning,
        stacklevel=2,
    )
