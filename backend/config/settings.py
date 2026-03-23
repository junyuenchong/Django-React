from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


def env(name: str, default=None):
    return os.getenv(name, default)


SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-secret-not-for-production")
DEBUG = env("DJANGO_DEBUG", "0") in ("1", "true", "True", "yes", "on")

ALLOWED_HOSTS = [h for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "apps.items.apps.ItemsConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "appdb"),
        "USER": env("POSTGRES_USER", "appuser"),
        "PASSWORD": env("POSTGRES_PASSWORD", "apppass"),
        "HOST": env("POSTGRES_HOST", "db"),
        "PORT": env("POSTGRES_PORT", "5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = env("DJANGO_STATIC_ROOT", str(BASE_DIR / "staticfiles"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


def parse_csv(name: str, default: str) -> list[str]:
    raw = env(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


# Backend-only default CORS origin.
# If you run the frontend on another origin, update `CORS_ALLOWED_ORIGINS`.
CORS_ALLOWED_ORIGINS = parse_csv("CORS_ALLOWED_ORIGINS", "http://localhost:8000")
CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL", "0") in ("1", "true", "True", "yes", "on")
ITEMS_LIST_CACHE_TTL_SECONDS = int(env("ITEMS_LIST_CACHE_TTL_SECONDS", "300"))


CACHE_BACKEND = env("CACHE_BACKEND", "redis").lower()
if CACHE_BACKEND == "redis":
    REDIS_HOST = env("REDIS_HOST", "redis")
    REDIS_PORT = env("REDIS_PORT", "6379")
    REDIS_DB = env("REDIS_DB", "0")
    REDIS_SOCKET_CONNECT_TIMEOUT = float(env("REDIS_SOCKET_CONNECT_TIMEOUT", "2"))
    REDIS_SOCKET_TIMEOUT = float(env("REDIS_SOCKET_TIMEOUT", "2"))
    REDIS_MAX_CONNECTIONS = int(env("REDIS_MAX_CONNECTIONS", "100"))
    REDIS_RETRY_ON_TIMEOUT = env("REDIS_RETRY_ON_TIMEOUT", "1") in ("1", "true", "True", "yes", "on")
    REDIS_KEY_PREFIX = env("REDIS_KEY_PREFIX", "react_django")
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
            "TIMEOUT": ITEMS_LIST_CACHE_TTL_SECONDS,
            "KEY_PREFIX": REDIS_KEY_PREFIX,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": REDIS_SOCKET_CONNECT_TIMEOUT,
                "SOCKET_TIMEOUT": REDIS_SOCKET_TIMEOUT,
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": REDIS_MAX_CONNECTIONS,
                    "retry_on_timeout": REDIS_RETRY_ON_TIMEOUT,
                },
                "IGNORE_EXCEPTIONS": True,
            },
        }
    }
else:
    # For local/unit tests, avoid external cache dependencies.
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.ItemCursorPagination",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "EXCEPTION_HANDLER": "config.exceptions.api_exception_handler",
    # This is an interview-style CRUD demo.
    # Authentication is disabled to keep the React integration simple.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
}

