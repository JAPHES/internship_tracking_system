from .base import *  # noqa: F403

DEBUG = env.bool("DEBUG", default=True)  # noqa: F405

MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE  # noqa: F405
    if middleware != "whitenoise.middleware.WhiteNoiseMiddleware"
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
