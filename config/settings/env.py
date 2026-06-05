"""Small typed helpers for reading environment variables.

Kept dependency-free on purpose: docker-compose injects real values via
``env_file``, while the defaults in ``base.py`` keep local runs working.
"""
import os

_TRUE = {"1", "true", "yes", "on"}


def env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)


def env_bool(key: str, default: bool) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in _TRUE


def env_list(key: str, default: list[str], sep: str = ",") -> list[str]:
    value = os.environ.get(key)
    if value is None:
        return default
    return [item.strip() for item in value.split(sep) if item.strip()]
