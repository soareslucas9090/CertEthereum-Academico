import os
import sys
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
SECRET_KEY = os.environ.get("SECRETE_KEY_DJANGO")
# Testa se já há variáveis de ambiente configuradas, se não há, carrega do arquivo local .env
if not SECRET_KEY:
    load_dotenv()
    SECRET_KEY = os.environ.get("SECRETE_KEY_DJANGO")

DEBUG = os.environ.get("DEBUG_MODE")
ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS")]
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("BD_ENGINE"),
        "NAME": os.environ.get("BD_NAME"),
        "USER": os.environ.get("BD_USER"),
        "PASSWORD": os.environ.get("BD_PASS"),
        "HOST": os.environ.get("BD_HOST"),
        "PORT": os.environ.get("BD_PORT"),
    }
}
signing_key = str(os.environ.get("SECRETE_KEY_JWT"))

LOGIN_REDIRECT_URL = "/redirect/"

SESSION_COOKIE_AGE = 1800

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

AUTH_USER_MODEL = "certificados.Users"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

INTERNAL_IPS = [
    "127.0.0.1",
]

CORS_ORIGIN_WHITELIST = [
    "https://cloud.seenode.com",
    "http://127.0.0.1",
    "https://127.0.0.1",
]

CORS_ALLOWED_HOSTS = [
    "https://cloud.seenode.com",
    "http://127.0.0.1",
    "https://127.0.0.1",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://cloud.seenode.com",
    "http://127.0.0.1",
    "https://127.0.0.1",
]

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_METHODS = ["*"]

if "test" in sys.argv or "test_coverage" in sys.argv:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "certificados",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "certethereum.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "certethereum.wsgi.application"

SPECTACULAR_SETTINGS = {
    "TITLE": "Your Project API",
    "DESCRIPTION": "Your project description",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "TAGS": [
        {"name": "Auth", "description": "Authentication related endpoints."},
        {
            "name": "Issue Certificate",
            "description": "The POST endpoint to issue certificates.",
        },
        {
            "name": "Search",
            "description": "The GET endpoint to search certificates by hash or CPF.",
        },
        {
            "name": "Users",
            "description": "Users related endpoints.",
        },
    ],
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DATE_INPUT_FORMATS": ["%Y/%m/%d", "%Y-%m-%d"],
    "TIME_INPUT_FORMATS": [
        "%H:%M",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=240),
    "BLACKLIST_AFTER_ROTATION": False,
    "SIGNING_KEY": signing_key,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
