"""
Production settings for pdf_reader project.
This file contains production-specific settings that override development settings.
"""

from .settings import *

# Production Security Settings
DEBUG = False

# SSL/HTTPS Security - Force HTTPS in production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie Security - Force secure cookies in production
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Additional Production Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Production Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'main': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# Production Database - Use environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='pdf_reader_db'),
        'USER': config('DB_USER', default='pdf_reader_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Production Static Files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Production Media Files
MEDIA_ROOT = BASE_DIR / 'media'

# Security: Hide secret key
SECRET_KEY = config('SECRET_KEY')

# Allowed hosts for production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='mathivarman.pythonanywhere.com').split(',')

# CSRF trusted origins for production
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://mathivarman.pythonanywhere.com').split(',')
