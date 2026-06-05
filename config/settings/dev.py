"""Local development settings."""
from .base import *  # noqa: F401,F403
from .env import env_bool

DEBUG = env_bool("DJANGO_DEBUG", True)

# Convenience for local API exploration.
ALLOWED_HOSTS = ["*"]

# Browsable API + sessions are handy during development.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
