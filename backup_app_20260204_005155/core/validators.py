"""
Input validation utilities
"""

from __future__ import annotations

import re
from urllib.parse import urlparse
from app.core.constants import MAX_PATH_LENGTH, MAX_URL_LENGTH, MAX_ID_LENGTH


class InputValidationError(ValueError):
    """Input validation error"""


_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x1F\x7F]")
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")


def _validate_basic_string(value: str, field_name: str, max_length: int) -> str:
    if value is None:
        raise InputValidationError(f"{field_name} is required")
    if not isinstance(value, str):
        raise InputValidationError(f"{field_name} must be a string")
    v = value.strip()
    if not v:
        raise InputValidationError(f"{field_name} is required")
    if len(v) > max_length:
        raise InputValidationError(f"{field_name} length must be <= {max_length}")
    if _CONTROL_CHAR_PATTERN.search(v):
        raise InputValidationError(f"{field_name} contains invalid characters")
    return v


def validate_path(value: str, field_name: str = "path", max_length: int = MAX_PATH_LENGTH) -> str:
    return _validate_basic_string(value, field_name, max_length)


def validate_identifier(value: str, field_name: str = "id", max_length: int = MAX_ID_LENGTH) -> str:
    v = _validate_basic_string(value, field_name, max_length)
    if not _ID_PATTERN.match(v):
        raise InputValidationError(f"{field_name} has invalid format")
    return v


def validate_http_url(value: str, field_name: str = "url", max_length: int = MAX_URL_LENGTH) -> str:
    v = _validate_basic_string(value, field_name, max_length)
    parsed = urlparse(v)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise InputValidationError(f"{field_name} must be a valid http/https URL")
    return v


def validate_proxy_path(value: str, field_name: str = "path", max_length: int = MAX_URL_LENGTH) -> str:
    v = _validate_basic_string(value, field_name, max_length)
    if "://" in v or v.startswith("//"):
        raise InputValidationError(f"{field_name} contains invalid scheme")
    parts = [p for p in v.split("/") if p]
    if any(p == ".." for p in parts):
        raise InputValidationError(f"{field_name} contains invalid path segment")
    return v
