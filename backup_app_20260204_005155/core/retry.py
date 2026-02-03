"""
Unified retry policy
"""

from __future__ import annotations

import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.constants import (
    RETRY_MAX_ATTEMPTS,
    RETRY_MIN_SECONDS,
    RETRY_MAX_SECONDS,
    RETRY_MULTIPLIER,
)


class TransientError(Exception):
    """Retryable transient error"""


def retry_on_transient():
    """Return a retry decorator for async functions."""
    return retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(
            multiplier=RETRY_MULTIPLIER,
            min=RETRY_MIN_SECONDS,
            max=RETRY_MAX_SECONDS,
        ),
        retry=retry_if_exception_type(
            (aiohttp.ClientError, asyncio.TimeoutError, TransientError)
        ),
        reraise=True,
    )
