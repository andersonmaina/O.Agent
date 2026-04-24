"""
Validation utilities for common data types
"""

import re
from datetime import datetime
from typing import Optional


def is_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_phone(phone: str) -> bool:
    """Validate phone number (various formats)."""
    pattern = r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$'
    return re.match(pattern, re.sub(r'\s', '', phone)) is not None


def is_credit_card(card_number: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    card_number = re.sub(r'\D', '', card_number)
    if not card_number.isdigit():
        return False
    
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    total = sum(odd_digits)
    for digit in even_digits:
        digit *= 2
        if digit > 9:
            digit -= 9
        total += digit
    
    return total % 10 == 0


def is_strong_password(password: str, min_length: int = 8) -> bool:
    """Check if password meets strength requirements."""
    if len(password) < min_length:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    return has_upper and has_lower and has_digit and has_special


def is_valid_date(date_str: str, format_str: str = '%Y-%m-%d') -> bool:
    """Validate date string format."""
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def is_numeric(value: str) -> bool:
    """Check if string is numeric."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_integer(value: str) -> bool:
    """Check if string is an integer."""
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_alphanumeric(text: str) -> bool:
    """Check if string is alphanumeric."""
    return text.isalnum()


def is_alpha(text: str) -> bool:
    """Check if string contains only letters."""
    return text.isalpha()


def is_empty(value: any) -> bool:
    """Check if value is empty."""
    if value is None:
        return True
    if isinstance(value, str):
        return len(value.strip()) == 0
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def is_not_empty(value: any) -> bool:
    """Check if value is not empty."""
    return not is_empty(value)


def is_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$'
    return re.match(pattern, url, re.IGNORECASE) is not None


def is_ipv4(ip: str) -> bool:
    """Validate IPv4 address."""
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None


def is_ipv6(ip: str) -> bool:
    """Validate IPv6 address."""
    pattern = r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'
    return re.match(pattern, ip) is not None


def is_uuid(value: str) -> bool:
    """Validate UUID format."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(pattern, value.lower()) is not None


def is_hex(value: str) -> bool:
    """Check if string is valid hexadecimal."""
    pattern = r'^[0-9a-fA-F]+$'
    return re.match(pattern, value) is not None


def is_base64(value: str) -> bool:
    """Check if string is valid base64."""
    pattern = r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'
    return re.match(pattern, value) is not None


def is_slug(value: str) -> bool:
    """Check if string is a valid slug."""
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return re.match(pattern, value) is not None


def is_username(value: str, min_length: int = 3, max_length: int = 20) -> bool:
    """Validate username format."""
    if not min_length <= len(value) <= max_length:
        return False
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    return re.match(pattern, value) is not None


def is_file_extension(value: str) -> bool:
    """Check if string is a valid file extension."""
    pattern = r'^[a-zA-Z0-9]+$'
    return re.match(pattern, value.lstrip('.')) is not None


def is_in_range(value: float, min_val: float, max_val: float) -> bool:
    """Check if numeric value is within range."""
    return min_val <= value <= max_val


def is_positive(value: float) -> bool:
    """Check if number is positive."""
    return value > 0


def is_negative(value: float) -> bool:
    """Check if number is negative."""
    return value < 0


def is_zero(value: float) -> bool:
    """Check if number is zero."""
    return value == 0
