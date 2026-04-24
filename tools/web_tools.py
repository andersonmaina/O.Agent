"""
Web utilities and URL manipulation tools
"""

import re
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, quote, unquote
from typing import Dict, List, Optional


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and pattern.match(url) is not None


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc or parsed.path.split('/')[0]


def extract_path(url: str) -> str:
    """Extract path from URL."""
    parsed = urlparse(url)
    return parsed.path


def parse_query_params(url: str) -> Dict[str, List[str]]:
    """Parse query parameters from URL."""
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def build_url(base: str, path: str = None, params: Dict = None) -> str:
    """Build a URL from components."""
    if path:
        base = urljoin(base, path)
    if params:
        query = urlencode(params, doseq=True)
        separator = '&' if '?' in base else '?'
        base = f"{base}{separator}{query}"
    return base


def is_url_safe(url: str, allowed_domains: List[str] = None) -> bool:
    """Check if URL is safe (not malicious)."""
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


def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments and standardizing format."""
    parsed = urlparse(url)
    # Remove fragment
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized


def extract_urls_from_text(text: str) -> List[str]:
    """Extract all URLs from text."""
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)


def url_encode(text: str) -> str:
    """URL encode a string."""
    return quote(text, safe='')


def url_decode(text: str) -> str:
    """URL decode a string."""
    return unquote(text)


def get_url_components(url: str) -> Dict[str, str]:
    """Get all components of a URL."""
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
        'port': parsed.port or ''
    }


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs have the same domain."""
    return extract_domain(url1) == extract_domain(url2)


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """Convert relative URL to absolute URL."""
    return urljoin(base_url, relative_url)


def sanitize_url(url: str) -> str:
    """Sanitize URL by removing potentially dangerous characters."""
    # Remove javascript: and data: schemes
    url = re.sub(r'^(javascript|data|vbscript):', 'http:', url, flags=re.IGNORECASE)
    return url
