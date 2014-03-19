"""
Django settings for bikeme project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


from project_runpy import env
import dj_database_url


ENVIRONMENT = env.get('ENVIRONMENT')

SECRET_KEY = env.get('SECRET_KEY', '12345')

DEBUG = env.get('DEBUG', False)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']  # XXX

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'south',

    'bikeme.apps.core',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bikeme.urls'

WSGI_APPLICATION = 'bikeme.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///bikeme.db')
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static_root'

STATICFILES_DIRS = (
    # os.path.join(BASE_DIR, 'static'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'project_runpy.ColorizingStreamHandler',
        },
    },
    'filters': {
        'readable_sql': {
            '()': 'project_runpy.ReadableSqlFilter',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', ],
            'level': 'DEBUG',
            'filters': ['readable_sql', ],
        },
    },
}


if env.get('SENTRY_DSN'):
    RAVEN_CONFIG = {
        'dsn': env.get('SENTRY_DSN'),
    }
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')


if ENVIRONMENT == 'test':
    DEBUG = False
    DATABASES['default'] = dj_database_url.parse('sqlite:///:memory:')
    INSTALLED_APPS.remove('south')
    LOGGING['loggers']['django.db.backends']['level'] = 'ERROR'
