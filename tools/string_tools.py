"""
String manipulation and text utilities
"""

import re
from typing import List, Optional


def slugify(text: str, separator: str = '-') -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', separator, text)
    return text


def camel_case(text: str) -> str:
    """Convert text to camelCase."""
    words = re.split(r'[-_\s]+', text.lower())
    return words[0] + ''.join(word.capitalize() for word in words[1:])


def pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    words = re.split(r'[-_\s]+', text.lower())
    return ''.join(word.capitalize() for word in words)


def snake_case(text: str) -> str:
    """Convert text to snake_case."""
    text = re.sub(r'[-\s]+', '_', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
    return text.lower().strip('_')


def kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    text = re.sub(r'[_\s]+', '-', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1-\2', text)
    return text.lower().strip('-')


def truncate(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r'<[^>]+>', '', text)


def remove_special_chars(text: str, keep_spaces: bool = True) -> str:
    """Remove special characters from text."""
    if keep_spaces:
        return re.sub(r'[^\w\s]', '', text)
    return re.sub(r'[^\w]', '', text)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def is_palindrome(text: str, ignore_case: bool = True, ignore_spaces: bool = True) -> bool:
    """Check if text is a palindrome."""
    if ignore_case:
        text = text.lower()
    if ignore_spaces:
        text = text.replace(' ', '')
    text = re.sub(r'[^\w]', '', text)
    return text == text[::-1]


def word_frequency(text: str, top_n: int = None) -> dict:
    """Get word frequency in text."""
    from collections import Counter
    words = re.findall(r'\b\w+\b', text.lower())
    counter = Counter(words)
    if top_n:
        return dict(counter.most_common(top_n))
    return dict(counter)


def character_frequency(text: str) -> dict:
    """Get character frequency in text."""
    from collections import Counter
    return dict(Counter(text))


def remove_whitespace(text: str) -> str:
    """Remove all whitespace from text."""
    return ''.join(text.split())


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace (multiple spaces to single)."""
    return ' '.join(text.split())


def pad_left(text: str, length: int, char: str = ' ') -> str:
    """Pad text on the left to specified length."""
    return text.rjust(length, char)


def pad_right(text: str, length: int, char: str = ' ') -> str:
    """Pad text on the right to specified length."""
    return text.ljust(length, char)


def pad_center(text: str, length: int, char: str = ' ') -> str:
    """Center text to specified length."""
    return text.center(length, char)


def remove_accents(text: str) -> str:
    """Remove accents from text."""
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', text) 
                   if unicodedata.category(c) != 'Mn')


def is_uppercase(text: str) -> bool:
    """Check if all characters are uppercase."""
    return text.isupper()


def is_lowercase(text: str) -> bool:
    """Check if all characters are lowercase."""
    return text.islower()


def is_title_case(text: str) -> bool:
    """Check if text is in title case."""
    return text.istitle()


def swap_case(text: str) -> str:
    """Swap case of all characters."""
    return text.swapcase()


def repeat_string(text: str, n: int) -> str:
    """Repeat string n times."""
    return text * n


def insert_string(text: str, insert: str, position: int) -> str:
    """Insert string at specified position."""
    return text[:position] + insert + text[position:]


def replace_all(text: str, replacements: dict) -> str:
    """Replace multiple substrings at once."""
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def extract_between(text: str, start: str, end: str) -> List[str]:
    """Extract all text between start and end delimiters."""
    pattern = re.escape(start) + r'(.*?)' + re.escape(end)
    return re.findall(pattern, text, re.DOTALL)


def count_substring(text: str, substring: str) -> int:
    """Count occurrences of substring in text."""
    return text.count(substring)


def starts_with_any(text: str, prefixes: List[str]) -> bool:
    """Check if text starts with any of the prefixes."""
    return any(text.startswith(prefix) for prefix in prefixes)


def ends_with_any(text: str, suffixes: List[str]) -> bool:
    """Check if text ends with any of the suffixes."""
    return any(text.endswith(suffix) for suffix in suffixes)
