"""
Cryptography and security utilities
"""

import hashlib
import base64
import secrets
import string
import uuid
from typing import Optional


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """Hash a string using specified algorithm."""
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
        'sha224': hashlib.sha224,
        'sha384': hashlib.sha384,
    }
    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    return algorithms[algorithm](text.encode()).hexdigest()


def verify_hash(text: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
    """Verify if text matches expected hash."""
    return hash_string(text, algorithm) == expected_hash


def generate_random_string(length: int = 32, use_letters: bool = True, 
                           use_digits: bool = True, use_symbols: bool = False) -> str:
    """Generate a cryptographically secure random string."""
    chars = ''
    if use_letters:
        chars += string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation
    if not chars:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_uuid() -> str:
    """Generate a UUID v4."""
    return str(uuid.uuid4())


def generate_token(length: int = 32) -> str:
    """Generate a secure random token (URL-safe)."""
    return secrets.token_urlsafe(length)


def base64_encode(text: str) -> str:
    """Encode text to base64."""
    return base64.b64encode(text.encode()).decode()


def base64_decode(encoded: str) -> str:
    """Decode base64 to text."""
    return base64.b64decode(encoded.encode()).decode()


def base64_url_encode(text: str) -> str:
    """Encode text to URL-safe base64."""
    return base64.urlsafe_b64encode(text.encode()).decode()


def base64_url_decode(encoded: str) -> str:
    """Decode URL-safe base64 to text."""
    return base64.urlsafe_b64decode(encoded.encode()).decode()


def hmac_hash(text: str, key: str, algorithm: str = 'sha256') -> str:
    """Create HMAC hash of text with key."""
    import hmac
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
    }
    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    return hmac.new(key.encode(), text.encode(), algorithms[algorithm]).hexdigest()


def generate_password(length: int = 16, use_special: bool = True) -> str:
    """Generate a strong random password."""
    chars = string.ascii_letters + string.digits
    if use_special:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    # Ensure at least one of each type
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
    ]
    if use_special:
        password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
    password += [secrets.choice(chars) for _ in range(length - len(password))]
    # Shuffle
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)


def mask_string(text: str, visible_chars: int = 4, mask_char: str = '*') -> str:
    """Mask a string (useful for passwords, API keys)."""
    if len(text) <= visible_chars:
        return mask_char * len(text)
    return mask_char * (len(text) - visible_chars) + text[-visible_chars:]


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time (prevent timing attacks)."""
    return secrets.compare_digest(a, b)


def generate_api_key(prefix: str = 'sk') -> str:
    """Generate an API key with prefix."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"
