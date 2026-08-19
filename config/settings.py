from pathlib import Path
import environ
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')




SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.mfa',
    'axes',
    'storages',
    'django_ckeditor_5',

    'accounts',
    'blog',
    'dashboard',
    'core',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]



ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_ENABLED = False
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/300s',
}

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'


AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # horas de bloqueo tras exceder el limite
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']

SESSION_COOKIE_AGE = 60 * 60 * 4  # 4 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

MFA_SUPPORTED_TYPES = ['totp', 'recovery_codes']
MFA_PASSKEY_LOGIN_ENABLED = False


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'



DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
AUTH_USER_MODEL = 'accounts.User'
SITE_ID = 1

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
if not DEBUG:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
    }

    AWS_ACCESS_KEY_ID = env('R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('R2_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = env('R2_ENDPOINT_URL')
    AWS_S3_CUSTOM_DOMAIN = env('R2_PUBLIC_DOMAIN')
    AWS_S3_REGION_NAME = 'auto'
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_ADDRESSING_STYLE = 'virtual'


if DEBUG:
    MAILERS = {
        'default': {
            'BACKEND': 'django.core.mail.backends.console.EmailBackend',
        },
    }
else:
    MAILERS = {
        'default': {
            'BACKEND': 'core.email_backends.ResendEmailBackend',
            'OPTIONS': {
                'api_key': env('RESEND_API_KEY'),
            },
        },
    }

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='no-reply@wcrafter.com')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}



CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'link', 'bulletedList', 'numberedList', '|',
            'blockQuote', 'insertImage', 'mediaEmbed', '|',
            'undo', 'redo',
        ],
    },
}
if DEBUG:
    CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    CKEDITOR_5_FILE_STORAGE = 'storages.backends.s3.S3Storage'