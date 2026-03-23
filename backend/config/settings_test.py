from .settings import *  # noqa: F403


DEBUG = False


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Tests should not depend on external Redis.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


# Speed up test runs.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

