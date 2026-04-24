"""
Data processing and manipulation utilities
"""

import json
import csv
import io
from collections import defaultdict
from typing import Any, Dict, List


def parse_csv(content: str, delimiter: str = ',') -> list:
    """Parse CSV content and return list of dictionaries."""
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    return list(reader)


def write_csv(data: list, fieldnames: list = None) -> str:
    """Write list of dictionaries to CSV format."""
    if not data:
        return ''
    if fieldnames is None:
        fieldnames = list(data[0].keys())
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def parse_json(content: str) -> Any:
    """Parse JSON string and return Python object."""
    return json.loads(content)


def write_json(data: Any, indent: int = 2, sort_keys: bool = False) -> str:
    """Convert Python object to JSON string."""
    return json.dumps(data, indent=indent, sort_keys=sort_keys)


def parse_xml(content: str) -> dict:
    """Simple XML parser (basic implementation)."""
    import re
    result = {}
    pattern = r'<(\w+)([^>]*)>(.*?)</\1>|<(\w+)([^>]*)/>'
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        if match[0]:  # Regular tag
            tag, attrs, content_text = match[0], match[1], match[2]
            result[tag] = content_text.strip()
        else:  # Self-closing tag
            tag = match[3]
            result[tag] = ''
    return result


def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def merge_dicts(*dicts, overwrite: bool = True) -> dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if overwrite:
            result.update(d)
        else:
            for k, v in d.items():
                if k not in result:
                    result[k] = v
    return result


def filter_dict(d: dict, keys: list = None, exclude: list = None) -> dict:
    """Filter dictionary by including or excluding keys."""
    if keys:
        return {k: v for k, v in d.items() if k in keys}
    if exclude:
        return {k: v for k, v in d.items() if k not in exclude}
    return d


def sort_dict(d: dict, by: str = 'key', reverse: bool = False) -> dict:
    """Sort dictionary by key or value."""
    if by == 'key':
        return dict(sorted(d.items(), key=lambda x: x[0], reverse=reverse))
    elif by == 'value':
        return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))
    return d


def group_by(items: list, key_func) -> dict:
    """Group list items by key function."""
    grouped = defaultdict(list)
    for item in items:
        key = key_func(item)
        grouped[key].append(item)
    return dict(grouped)


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def rotate_list(lst: list, n: int) -> list:
    """Rotate list by n positions."""
    if not lst:
        return lst
    n = n % len(lst)
    return lst[n:] + lst[:n]


def unique_list(lst: list) -> list:
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def intersection(*lists) -> list:
    """Find intersection of multiple lists."""
    if not lists:
        return []
    result = set(lists[0])
    for lst in lists[1:]:
        result &= set(lst)
    return list(result)


def union(*lists) -> list:
    """Find union of multiple lists."""
    result = set()
    for lst in lists:
        result.update(lst)
    return list(result)


def difference(list1: list, list2: list) -> list:
    """Find elements in list1 but not in list2."""
    return list(set(list1) - set(list2))


def zip_dicts(*dicts) -> dict:
    """Zip multiple dictionaries together."""
    result = defaultdict(list)
    for d in dicts:
        for k, v in d.items():
            result[k].append(v)
    return dict(result)


def invert_dict(d: dict) -> dict:
    """Invert dictionary (swap keys and values)."""
    return {v: k for k, v in d.items()}


def deep_copy(obj: Any) -> Any:
    """Create a deep copy of object."""
    import copy
    return copy.deepcopy(obj)


def dict_to_list(d: dict, key_name: str = 'key', value_name: str = 'value') -> list:
    """Convert dictionary to list of dictionaries."""
    return [{key_name: k, value_name: v} for k, v in d.items()]


def list_to_dict(lst: list, key_field: str, value_field: str = None) -> dict:
    """Convert list of dictionaries to dictionary."""
    if value_field:
        return {item[key_field]: item[value_field] for item in lst}
    return {item[key_field]: item for item in lst}


def safe_get(d: dict, key: str, default: Any = None) -> Any:
    """Safely get value from nested dictionary."""
    keys = key.split('.')
    current = d
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    return current


def set_nested(d: dict, key: str, value: Any) -> dict:
    """Set value in nested dictionary."""
    keys = key.split('.')
    current = d
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value
    return d
