"""
Text processing and manipulation utilities
"""

import re
import random
from collections import Counter


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_lines(text: str) -> int:
    """Count lines in text."""
    return len(text.splitlines())


def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count characters in text."""
    if include_spaces:
        return len(text)
    return len(text.replace(' ', ''))


def extract_emails(text: str) -> list:
    """Extract all email addresses from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def extract_urls(text: str) -> list:
    """Extract all URLs from text."""
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)


def extract_phone_numbers(text: str) -> list:
    """Extract phone numbers from text (various formats)."""
    pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    return re.findall(pattern, text)


def remove_duplicates(text: str, by_line: bool = True) -> str:
    """Remove duplicate lines or words from text."""
    if by_line:
        lines = text.splitlines()
        seen = set()
        unique = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique.append(line)
        return '\n'.join(unique)
    else:
        words = text.split()
        seen = set()
        unique = []
        for word in words:
            if word not in seen:
                seen.add(word)
                unique.append(word)
        return ' '.join(unique)


def shuffle_text(text: str, by_word: bool = True) -> str:
    """Shuffle words or characters in text."""
    if by_word:
        words = text.split()
        random.shuffle(words)
        return ' '.join(words)
    else:
        chars = list(text)
        random.shuffle(chars)
        return ''.join(chars)


def reverse_text(text: str, by_word: bool = False) -> str:
    """Reverse text or words in text."""
    if by_word:
        words = text.split()
        return ' '.join(reversed(words))
    return text[::-1]


def capitalize_words(text: str, title_case: bool = False) -> str:
    """Capitalize all words in text."""
    if title_case:
        return text.title()
    return text.upper()


def lowercase_words(text: str) -> str:
    """Convert all text to lowercase."""
    return text.lower()


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def wrap_text(text: str, width: int = 80) -> str:
    """Wrap text to specified width."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def indent_text(text: str, spaces: int = 4) -> str:
    """Indent all lines in text."""
    indent = ' ' * spaces
    return '\n'.join(indent + line for line in text.splitlines())


def remove_empty_lines(text: str) -> str:
    """Remove empty lines from text."""
    lines = [line for line in text.splitlines() if line.strip()]
    return '\n'.join(lines)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return ' '.join(text.split())


def extract_hashtags(text: str) -> list:
    """Extract hashtags from text."""
    pattern = r'#\w+'
    return re.findall(pattern, text)


def extract_mentions(text: str) -> list:
    """Extract @mentions from text."""
    pattern = r'@\w+'
    return re.findall(pattern, text)


def word_frequency(text: str, top_n: int = None) -> dict:
    """Get word frequency in text."""
    words = re.findall(r'\b\w+\b', text.lower())
    counter = Counter(words)
    if top_n:
        return dict(counter.most_common(top_n))
    return dict(counter)


def sentence_count(text: str) -> int:
    """Count sentences in text."""
    pattern = r'[.!?]+'
    return len(re.findall(pattern, text))


def average_word_length(text: str) -> float:
    """Calculate average word length."""
    words = text.split()
    if not words:
        return 0.0
    total_length = sum(len(word) for word in words)
    return total_length / len(words)


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    pattern = r'<[^>]+>'
    return re.sub(pattern, '', text)


def strip_html(text: str) -> str:
    """Alias for remove_html_tags."""
    return remove_html_tags(text)
