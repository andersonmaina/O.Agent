"""
Advanced search and discovery tools
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from smolagents import tool
import json


@tool
def semantic_search_tool(directory: str, query: str, file_pattern: str = '*',
                        max_results: int = 10) -> str:
    """Search files for content matching a query (keyword-based).
    Args:
        directory: Relative path to directory.
        query: Search keywords.
        file_pattern: Glob pattern (default '*').
        max_results: Maximum results to return (default 10).
    """
    try:
        results = semantic_search(directory, query, file_pattern, max_results)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error: {e}"


@tool
def grep_search_tool(pattern: str, directory: str = '.', file_pattern: str = '*',
                     case_sensitive: bool = False) -> str:
    """Search files using regex pattern matching.
    Args:
        pattern: Regex pattern to search for.
        directory: Relative path to directory.
        file_pattern: Glob pattern for files.
        case_sensitive: Whether match is case sensitive.
    """
    try:
        results = grep_search(pattern, directory, file_pattern, case_sensitive)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error: {e}"


def semantic_search(directory: str, query: str, file_pattern: str = '*',
                    max_results: int = 10) -> List[Dict[str, Any]]:
    """Search files for content matching a query (keyword-based semantic search)."""
    results = []
    query_terms = query.lower().split()

    for file_path in Path(directory).rglob(file_pattern):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        content_lower = content.lower()
        score = 0
        matches = []

        for term in query_terms:
            if term in content_lower:
                score += content_lower.count(term)
                matches.append(term)

        if score > 0:
            lines = content.split('\n')
            context_lines = []

            for i, line in enumerate(lines):
                if any(term in line.lower() for term in query_terms):
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    context_lines.append({
                        'line_number': i + 1,
                        'content': '...\n'.join(lines[start:end])
                    })

            results.append({
                'file': str(file_path),
                'score': score,
                'matched_terms': list(set(matches)),
                'context': context_lines[:3],
                'size': file_path.stat().st_size
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]


def grep_search(pattern: str, directory: str = '.', file_pattern: str = '*',
                case_sensitive: bool = False, max_results: int = 50) -> List[Dict[str, Any]]:
    """Search files using regex pattern matching."""
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return [{'error': f'Invalid regex: {e}'}]

    for file_path in Path(directory).rglob(file_pattern):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        lines = content.split('\n')
        file_matches = []

        for i, line in enumerate(lines):
            if regex.search(line):
                file_matches.append({
                    'line_number': i + 1,
                    'content': line.strip()[:200]
                })

        if file_matches:
            results.append({
                'file': str(file_path),
                'matches': file_matches[:10],
                'total_matches': len(file_matches)
            })

        if len(results) >= max_results:
            break

    return results


def search_by_type(file_type: str, directory: str = '.',
                   recursive: bool = True) -> List[str]:
    """Search for files by type/extension."""
    type_mapping = {
        'python': '*.py',
        'javascript': '*.js',
        'typescript': '*.ts',
        'json': '*.json',
        'yaml': '*.yaml',
        'yml': '*.yml',
        'xml': '*.xml',
        'html': '*.html',
        'css': '*.css',
        'markdown': '*.md',
        'text': '*.txt',
        'log': '*.log',
        'config': '*.cfg',
        'ini': '*.ini',
        'toml': '*.toml',
        'sql': '*.sql',
        'java': '*.java',
        'go': '*.go',
        'rust': '*.rs',
        'cpp': '*.cpp',
        'c': '*.c',
        'h': '*.h',
        'hpp': '*.hpp',
        'ruby': '*.rb',
        'php': '*.php',
        'shell': '*.sh',
        'bash': '*.bash',
    }

    pattern = type_mapping.get(file_type.lower(), f'*.{file_type}')

    if recursive:
        return [str(f) for f in Path(directory).rglob(pattern) if f.is_file()]
    return [str(f) for f in Path(directory).glob(pattern) if f.is_file()]


def find_duplicates(directory: str = '.', by_content: bool = False) -> List[List[str]]:
    """Find duplicate files in a directory."""
    if by_content:
        hash_map = {}

        for file_path in Path(directory).rglob('*'):
            if not file_path.is_file():
                continue

            try:
                import hashlib
                content = file_path.read_bytes()
                file_hash = hashlib.md5(content).hexdigest()

                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(str(file_path))
            except Exception:
                continue

        return [files for files in hash_map.values() if len(files) > 1]

    else:
        size_map = {}

        for file_path in Path(directory).rglob('*'):
            if not file_path.is_file():
                continue

            size = file_path.stat().st_size

            if size not in size_map:
                size_map[size] = []
            size_map[size].append(str(file_path))

        return [files for files in size_map.values() if len(files) > 1]


def search_recent(directory: str = '.', days: int = 7,
                  file_pattern: str = '*') -> List[Dict[str, Any]]:
    """Find recently modified files."""
    from datetime import timedelta

    cutoff = datetime.now() - timedelta(days=days)
    results = []

    for file_path in Path(directory).rglob(file_pattern):
        if not file_path.is_file():
            continue

        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

        if mtime > cutoff:
            results.append({
                'path': str(file_path),
                'modified': mtime.isoformat(),
                'size': file_path.stat().st_size,
                'days_ago': (datetime.now() - mtime).days
            })

    results.sort(key=lambda x: x['modified'], reverse=True)
    return results


def find_empty_files(directory: str = '.') -> List[str]:
    """Find all empty files in a directory."""
    return [str(f) for f in Path(directory).rglob('*')
            if f.is_file() and f.stat().st_size == 0]


def find_large_files(directory: str = '.', min_size_mb: float = 10) -> List[Dict[str, Any]]:
    """Find files larger than a specified size."""
    min_size_bytes = int(min_size_mb * 1024 * 1024)
    results = []

    for file_path in Path(directory).rglob('*'):
        if not file_path.is_file():
            continue

        size = file_path.stat().st_size

        if size >= min_size_bytes:
            results.append({
                'path': str(file_path),
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2)
            })

    results.sort(key=lambda x: x['size_bytes'], reverse=True)
    return results


def search_filenames(pattern: str, directory: str = '.',
                     case_sensitive: bool = False) -> List[str]:
    """Search for files by filename pattern."""
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return [f'Error: {e}']

    for file_path in Path(directory).rglob('*'):
        if regex.search(file_path.name):
            results.append(str(file_path))

    return results


def get_file_statistics(directory: str = '.') -> Dict[str, Any]:
    """Get statistics about files in a directory."""
    stats = {
        'total_files': 0,
        'total_directories': 0,
        'total_size': 0,
        'extensions': {},
        'largest_file': None,
        'oldest_file': None,
        'newest_file': None
    }

    for item in Path(directory).rglob('*'):
        if item.is_file():
            stats['total_files'] += 1
            size = item.stat().st_size
            stats['total_size'] += size

            ext = item.suffix.lower() or '(no extension)'
            stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1

            stat = item.stat()

            if stats['largest_file'] is None or size > stats['largest_file']['size']:
                stats['largest_file'] = {
                    'path': str(item),
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                }

            mtime = stat.st_mtime

            if stats['oldest_file'] is None or mtime < stats['oldest_file']['mtime']:
                stats['oldest_file'] = {
                    'path': str(item),
                    'modified': datetime.fromtimestamp(mtime).isoformat(),
                    'mtime': mtime
                }

            if stats['newest_file'] is None or mtime > stats['newest_file']['mtime']:
                stats['newest_file'] = {
                    'path': str(item),
                    'modified': datetime.fromtimestamp(mtime).isoformat(),
                    'mtime': mtime
                }

        elif item.is_dir():
            stats['total_directories'] += 1

    return stats

