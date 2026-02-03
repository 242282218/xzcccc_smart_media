"""
Constants
"""

REQUEST_ID_HEADER = "X-Request-ID"

# Input limits
MAX_PATH_LENGTH = 512
MAX_URL_LENGTH = 2048
MAX_ID_LENGTH = 128

MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 50
DEFAULT_BATCH_SIZE = 10

MIN_CONCURRENT_LIMIT = 1
MAX_CONCURRENT_LIMIT = 50

MIN_TIMEOUT_SECONDS = 1
MAX_TIMEOUT_SECONDS = 120

MAX_FILES_LIMIT = 1000

# Retry policy
RETRY_MAX_ATTEMPTS = 3
RETRY_MIN_SECONDS = 0.5
RETRY_MAX_SECONDS = 8
RETRY_MULTIPLIER = 0.5

# Sensitive field names (for masking)
SENSITIVE_FIELD_NAMES = {
    "password",
    "passwd",
    "token",
    "api_key",
    "apikey",
    "secret",
    "cookie",
    "authorization",
    "auth",
    "key",
}
