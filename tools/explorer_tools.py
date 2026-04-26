"""
Project exploration and codebase analysis tools
Similar to Claude Code's exploration capabilities
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from collections import defaultdict
from smolagents import tool


@tool
def explore_project(root_dir: str = '.', max_depth: int = 5) -> Dict[str, Any]:
    """
    Explore a project structure and return a comprehensive overview.
    Similar to Claude Code's project exploration.

    Args:
        root_dir: The root directory to explore.
        max_depth: Maximum folder depth to recurse into.
    """
    result = {
        'root': str(Path(root_dir).resolve()),
        'structure': {},
        'file_count': 0,
        'dir_count': 0,
        'total_size': 0,
        'languages': {},
        'entry_points': [],
        'config_files': []
    }

    ignore_patterns = {
        '.git', '__pycache__', 'node_modules', '.venv', 'venv',
        'dist', 'build', '.cache', '.pytest_cache', '.mypy_cache',
        '.idea', '.vscode', 'target', 'vendor', 'bin', 'obj'
    }

    ignore_extensions = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin'}

    entry_point_names = ['main.py', 'index.js', 'app.py', 'main.js', 'index.ts', 'app.js']
    config_names = ['package.json', 'pyproject.toml', 'setup.py', 'Cargo.toml',
                    'go.mod', 'pom.xml', 'build.gradle', 'CMakeLists.txt',
                    '.gitignore', '.env', 'config.json', 'settings.json']

    def _explore(path: Path, depth: int = 0) -> Optional[Dict]:
        if depth > max_depth:
            return None

        if path.name in ignore_patterns:
            return None

        if path.is_file():
            if path.suffix in ignore_extensions:
                return None

            rel_path = str(path.relative_to(Path(root_dir).resolve()))
            size = path.stat().st_size

            result['file_count'] += 1
            result['total_size'] += size

            ext = path.suffix.lower()
            result['languages'][ext] = result['languages'].get(ext, 0) + 1

            if path.name in entry_point_names:
                result['entry_points'].append(rel_path)

            if path.name in config_names or path.name.startswith('.'):
                result['config_files'].append(rel_path)

            return {'type': 'file', 'name': path.name, 'size': size}

        if path.is_dir():
            result['dir_count'] += 1

            node = {'type': 'directory', 'name': path.name, 'children': []}

            for child in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name)):
                child_node = _explore(child, depth + 1)
                if child_node:
                    node['children'].append(child_node)

            return node

        return None

    root_path = Path(root_dir).resolve()
    result['structure'] = _explore(root_path) or {}

    return result


@tool
def find_symbol(symbol_name: str, directory: str = '.',
                symbol_type: str = 'all') -> List[Dict[str, Any]]:
    """
    Find a symbol (function, class, variable) across the codebase.
    Similar to Claude Code's symbol search.

    Args:
        symbol_name: Name of the symbol to search for.
        directory: Directory to search in.
        symbol_type: 'all', 'class', 'function', or 'variable'.
    """
    results = []

    for file_path in Path(directory).rglob('*.py'):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            match = False
            node_type = None

            if symbol_type in ['all', 'class']:
                if isinstance(node, ast.ClassDef) and node.name == symbol_name:
                    match = True
                    node_type = 'class'

            if symbol_type in ['all', 'function']:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol_name:
                    match = True
                    node_type = 'function'

            if symbol_type in ['all', 'variable']:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == symbol_name:
                            match = True
                            node_type = 'variable'

            if match:
                results.append({
                    'file': str(file_path),
                    'line': node.lineno,
                    'type': node_type,
                    'name': symbol_name,
                    'context': _get_line_context(content, node.lineno)
                })

    return results


def _get_line_context(content: str, line_number: int, context_lines: int = 2) -> str:
    """Get surrounding context for a line."""
    lines = content.split('\n')
    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)
    return '\n'.join(lines[start:end])


@tool
def get_file_outline(file_path: str) -> List[Dict[str, Any]]:
    """
    Get an outline of a code file showing its structure.
    Similar to Claude Code's file outline feature.

    Args:
        file_path: Path to the source code file to outline.
    """
    try:
        content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        return []

    outline = []

    for node in ast.walk(tree):
        entry = None

        if isinstance(node, ast.ClassDef):
            methods = []
            for child in ast.walk(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(child.name)

            entry = {
                'type': 'class',
                'name': node.name,
                'line': node.lineno,
                'methods': methods
            }

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                args = [arg.arg for arg in node.args.args]
                entry = {
                    'type': 'function',
                    'name': node.name,
                    'line': node.lineno,
                    'parameters': args
                }

        if entry:
            outline.append(entry)

    outline.sort(key=lambda x: x['line'])
    return outline


@tool
def find_references(symbol_name: str, directory: str = '.') -> List[Dict[str, Any]]:
    """
    Find all references to a symbol in the codebase.
    Similar to Claude Code's find references feature.

    Args:
        symbol_name: Name of the symbol to find references for.
        directory: Directory to search in.
    """
    results = []

    for file_path in Path(directory).rglob('*'):
        if not file_path.is_file():
            continue

        if file_path.suffix not in ['.py', '.js', '.ts', '.jsx', '.tsx']:
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        pattern = r'\b' + re.escape(symbol_name) + r'\b'

        for i, line in enumerate(content.split('\n'), 1):
            if re.search(pattern, line):
                results.append({
                    'file': str(file_path),
                    'line': i,
                    'content': line.strip()[:100]
                })

    return results


@tool
def get_call_hierarchy(function_name: str, directory: str = '.') -> Dict[str, Any]:
    """
    Get the call hierarchy for a function - who calls it and what it calls.

    Args:
        function_name: Name of the function to analyze.
        directory: Directory to search in.
    """
    result = {
        'function': function_name,
        'called_by': [],
        'calls': []
    }

    for file_path in Path(directory).rglob('*.py'):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                result['calls'].append({
                                    'function': child.func.id,
                                    'file': str(file_path),
                                    'line': child.lineno
                                })

                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id == function_name:
                            result['called_by'].append({
                                'function': node.name,
                                'file': str(file_path),
                                'line': child.lineno
                            })

    return result


@tool
def find_implementation(interface_name: str, directory: str = '.') -> List[Dict[str, Any]]:
    """Find classes that implement a given interface/base class.

    Args:
        interface_name: Name of the interface or base class to search for.
        directory: Directory to search in.
    """
    results = []

    for file_path in Path(directory).rglob('*.py'):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = ast.unparse(base) if hasattr(ast, 'unparse') else str(base)
                    if interface_name in base_name:
                        results.append({
                            'class': node.name,
                            'file': str(file_path),
                            'line': node.lineno,
                            'base': base_name
                        })

    return results


@tool
def get_dependency_graph(directory: str = '.') -> Dict[str, List[str]]:
    """
    Build a dependency graph of imports in the project.

    Args:
        directory: Root directory of the project to analyze.
    """
    dependencies = defaultdict(set)

    for file_path in Path(directory).rglob('*.py'):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        module_name = file_path.stem

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies[module_name].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies[module_name].add(node.module)

    return {k: list(v) for k, v in dependencies.items()}


@tool
def analyze_codebase(directory: str = '.') -> Dict[str, Any]:
    """
    Comprehensive codebase analysis.
    Similar to Claude Code's deep codebase understanding.

    Args:
        directory: Root directory of the project to analyze.
    """
    result = {
        'overview': explore_project(directory),
        'entry_points': [],
        'test_files': [],
        'api_endpoints': [],
        'database_models': [],
        'complexity': {}
    }

    for file_path in Path(directory).rglob('*.py'):
        rel_path = str(file_path)

        if 'test' in file_path.name.lower():
            result['test_files'].append(rel_path)

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            if 'def ' in content:
                for match in re.finditer(r'@(?:app|router)\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']', content):
                    result['api_endpoints'].append({
                        'method': match.group(1),
                        'path': match.group(2),
                        'file': rel_path
                    })

            if 'class ' in content and ('Model' in content or 'SQLModel' in content):
                for match in re.finditer(r'class\s+(\w+).*?(?:Model|SQLModel)', content):
                    result['database_models'].append({
                        'name': match.group(1),
                        'file': rel_path
                    })

        except Exception:
            continue

    return result


@tool
def search_codebase(query: str, directory: str = '.',
                    max_results: int = 20) -> List[Dict[str, Any]]:
    """
    Search the codebase for relevant code based on a natural language query.
    Uses keyword matching and semantic analysis.

    Args:
        query: Natural language search query.
        directory: Root directory to search in.
        max_results: Maximum number of results to return.
    """
    results = []
    query_terms = query.lower().split()

    for file_path in Path(directory).rglob('*'):
        if not file_path.is_file():
            continue

        if file_path.suffix not in ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml']:
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        content_lower = content.lower()
        score = 0
        matched_terms = []

        for term in query_terms:
            if len(term) < 3:
                continue
            count = content_lower.count(term)
            if count > 0:
                score += count * len(term)
                matched_terms.append(term)

        if score > 0:
            lines = content.split('\n')
            best_lines = []

            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(term in line_lower for term in query_terms):
                    best_lines.append({
                        'line': i + 1,
                        'content': line.strip()[:150]
                    })

            results.append({
                'file': str(file_path),
                'score': score,
                'matched_terms': list(set(matched_terms)),
                'relevant_lines': best_lines[:5],
                'size': file_path.stat().st_size
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]
