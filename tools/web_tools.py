"""
Web utilities and URL manipulation tools
"""

import re
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, quote, unquote
from typing import Dict, List, Optional
from smolagents import tool


@tool
def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: The URL string to validate.
    """
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and pattern.match(url) is not None


@tool
def extract_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: The URL to extract the domain from.
    """
    parsed = urlparse(url)
    return parsed.netloc or parsed.path.split('/')[0]


@tool
def extract_path(url: str) -> str:
    """Extract path from URL.

    Args:
        url: The URL to extract the path from.
    """
    parsed = urlparse(url)
    return parsed.path


@tool
def parse_query_params(url: str) -> Dict[str, List[str]]:
    """Parse query parameters from URL.

    Args:
        url: The URL whose query parameters should be parsed.
    """
    parsed = urlparse(url)
    return parse_qs(parsed.query)


@tool
def build_url(base: str, path: str = None, params: Dict = None) -> str:
    """Build a URL from components.

    Args:
        base: The base URL.
        path: Optional path to append to the base URL.
        params: Optional dictionary of query parameters to add.
    """
    if path:
        base = urljoin(base, path)
    if params:
        query = urlencode(params, doseq=True)
        separator = '&' if '?' in base else '?'
        base = f"{base}{separator}{query}"
    return base


@tool
def is_url_safe(url: str, allowed_domains: List[str] = None) -> bool:
    """Check if URL is safe (not malicious).

    Args:
        url: The URL to check for safety.
        allowed_domains: Optional list of allowed domain names.
    """
    if not is_valid_url(url):
        return False

    parsed = urlparse(url)

    # Block dangerous schemes
    if parsed.scheme not in ['http', 'https']:
        return False

    # Check allowed domains if specified
    if allowed_domains:
        domain = parsed.netloc.split(':')[0]
        if domain not in allowed_domains:
            return False

    return True


@tool
def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments and standardizing format.

    Args:
        url: The URL to normalize.
    """
    parsed = urlparse(url)
    # Remove fragment
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized


@tool
def extract_urls_from_text(text: str) -> List[str]:
    """Extract all URLs from text.

    Args:
        text: The text to search for URLs.
    """
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)


@tool
def url_encode(text: str) -> str:
    """URL encode a string.

    Args:
        text: The string to URL-encode.
    """
    return quote(text, safe='')


@tool
def url_decode(text: str) -> str:
    """URL decode a string.

    Args:
        text: The URL-encoded string to decode.
    """
    return unquote(text)


@tool
def get_url_components(url: str) -> Dict[str, str]:
    """Get all components of a URL.

    Args:
        url: The URL to decompose into its components.
    """
    parsed = urlparse(url)
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'params': parsed.params,
        'query': parsed.query,
        'fragment': parsed.fragment,
        'username': parsed.username or '',
        'password': parsed.password or '',
        'hostname': parsed.hostname or '',
        'port': str(parsed.port) if parsed.port else ''
    }


@tool
def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs have the same domain.

    Args:
        url1: The first URL.
        url2: The second URL.
    """
    return extract_domain(url1) == extract_domain(url2)


@tool
def make_absolute_url(base_url: str, relative_url: str) -> str:
    """Convert relative URL to absolute URL.

    Args:
        base_url: The base URL to resolve against.
        relative_url: The relative URL to make absolute.
    """
    return urljoin(base_url, relative_url)


@tool
def sanitize_url(url: str) -> str:
    """Sanitize URL by removing potentially dangerous characters.

    Args:
        url: The URL to sanitize.
    """
    # Remove javascript: and data: schemes
    url = re.sub(r'^(javascript|data|vbscript):', 'http:', url, flags=re.IGNORECASE)
    return url
