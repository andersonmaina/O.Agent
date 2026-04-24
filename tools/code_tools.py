"""
Advanced code manipulation and analysis tools
"""

import ast
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


def analyze_code(code: str, language: str = 'python') -> Dict[str, Any]:
    """Analyze code structure and return metrics."""
    if language != 'python':
        return {'error': f'Language {language} not supported'}

    try:
        tree = ast.parse(code)

        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}.*" if node.module else "*")

        lines = code.split('\n')
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))

        return {
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'total_lines': len(lines),
            'code_lines': code_lines,
            'complexity': len(functions) + len(classes) * 2
        }
    except SyntaxError as e:
        return {'error': f'Syntax error: {e}'}


def find_code_patterns(code: str, pattern_type: str = 'all') -> List[str]:
    """Find specific patterns in code like TODOs, FIXMEs, function calls, etc."""
    patterns = {
        'todos': r'#\s*(TODO|FIXME|XXX|HACK|NOTE)[:\s]*(.*)',
        'functions': r'def\s+(\w+)\s*\(',
        'classes': r'class\s+(\w+)',
        'imports': r'(?:import|from)\s+([\w.]+)',
        'decorators': r'@(\w+)',
        'docstrings': r'"""(.*?)"""|\'\'\'(.*?)\'\'\'',
        'all': r'#\s*(TODO|FIXME|XXX|HACK|NOTE)[:\s]*(.*)|def\s+(\w+)\s*\(|class\s+(\w+)'
    }

    matches = []
    pattern = patterns.get(pattern_type, patterns['all'])
    for match in re.finditer(pattern, code, re.MULTILINE | re.DOTALL):
        matches.append(match.group(0))

    return matches


def refactor_variable(code: str, old_name: str, new_name: str) -> str:
    """Safely rename a variable throughout code."""
    # Simple word boundary replacement
    pattern = r'\b' + re.escape(old_name) + r'\b'
    return re.sub(pattern, new_name, code)


def extract_function(code: str, function_name: str) -> Optional[str]:
    """Extract a specific function from code."""
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return ast.unparse(node)
        return None
    except SyntaxError:
        return None


def generate_function_stub(name: str, params: List[str], return_type: str = 'None',
                           docstring: str = '') -> str:
    """Generate a function stub with proper typing."""
    params_str = ', '.join(params) if params else ''

    stub = f"def {name}({params_str}) -> {return_type}:\n"

    if docstring:
        stub += f'    """{docstring}"""\n'

    stub += '    pass\n'

    return stub


def validate_syntax(code: str, language: str = 'python') -> Dict[str, Any]:
    """Validate code syntax and return errors if any."""
    if language != 'python':
        return {'supported': False, 'error': f'Language {language} not supported'}

    try:
        ast.parse(code)
        return {'valid': True, 'error': None}
    except SyntaxError as e:
        return {'valid': False, 'error': f'Line {e.lineno}: {e.msg}'}


def count_code_metrics(code: str) -> Dict[str, int]:
    """Count various code metrics."""
    lines = code.split('\n')

    return {
        'total_lines': len(lines),
        'blank_lines': sum(1 for line in lines if not line.strip()),
        'comment_lines': sum(1 for line in lines if line.strip().startswith('#')),
        'code_lines': sum(1 for line in lines if line.strip() and not line.strip().startswith('#')),
        'characters': len(code),
        'functions': len(re.findall(r'def\s+\w+', code)),
        'classes': len(re.findall(r'class\s+\w+', code)),
        'decorators': len(re.findall(r'@\w+', code))
    }


def format_code(code: str, style: str = 'pep8') -> str:
    """Basic code formatting (simplified, not full black/autoformatter)."""
    lines = code.split('\n')
    formatted = []
    indent = 0

    for line in lines:
        stripped = line.strip()

        if stripped.endswith(':') and not stripped.startswith('#'):
            formatted.append('    ' * indent + stripped)
            indent += 1
        elif stripped in ['pass', 'return', 'break', 'continue']:
            indent = max(0, indent - 1)
            formatted.append('    ' * indent + stripped)
        elif stripped.startswith('return ') or stripped.startswith('yield '):
            indent = max(0, indent - 1)
            formatted.append('    ' * indent + stripped)
        else:
            if stripped and not stripped.startswith('#'):
                indent = max(0, indent - 1) if indent > 0 else 0
            formatted.append('    ' * indent + stripped)

    return '\n'.join(formatted)


def find_unused_imports(code: str) -> List[str]:
    """Find potentially unused imports in code."""
    try:
        tree = ast.parse(code)

        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports[alias.asname or alias.name] = alias.name

        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                used_names.add(node.attr)

        unused = [name for name, module in imports.items() if name not in used_names]
        return unused
    except SyntaxError:
        return []


def extract_classes(code: str) -> List[Dict[str, Any]]:
    """Extract all classes with their methods and attributes."""
    try:
        tree = ast.parse(code)
        classes = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                class_info = {
                    'name': node.name,
                    'bases': [ast.unparse(base) for base in node.bases],
                    'methods': methods,
                    'line': node.lineno
                }
                classes.append(class_info)

        return classes
    except SyntaxError:
        return []


def get_function_signature(code: str, function_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed function signature including parameters and return type."""
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                args = []
                for arg in node.args.args:
                    arg_info = {'name': arg.arg}
                    if arg.annotation:
                        arg_info['type'] = ast.unparse(arg.annotation)
                    args.append(arg_info)

                returns = None
                if node.returns:
                    returns = ast.unparse(node.returns)

                return {
                    'name': function_name,
                    'parameters': args,
                    'return_type': returns,
                    'decorators': [ast.unparse(d) for d in node.decorator_list],
                    'line': node.lineno
                }
        return None
    except SyntaxError:
        return None


def generate_docstring_template(code: str, function_name: str) -> Optional[str]:
    """Generate a docstring template for a function."""
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                returns = 'Returns' if node.returns else ''

                docstring = f'"""{function_name} - TODO: Add description\n\n'

                if params:
                    docstring += 'Args:\n'
                    for param in params:
                        docstring += f'        {param}: TODO: Describe parameter\n'

                if returns:
                    docstring += f'\n{returns}:\n        TODO: Describe return value\n'

                docstring += '"""'
                return docstring

        return None
    except SyntaxError:
        return None


def compare_code_similarity(code1: str, code2: str) -> float:
    """Calculate similarity between two code snippets (0.0 to 1.0)."""
    def normalize(code):
        code = re.sub(r'#.*', '', code)
        code = re.sub(r'["\']{3}.*?["\']{3}', '', code, flags=re.DOTALL)
        code = re.sub(r'\s+', ' ', code)
        return code.strip().lower()

    norm1 = normalize(code1)
    norm2 = normalize(code2)

    if not norm1 or not norm2:
        return 0.0

    tokens1 = set(norm1.split())
    tokens2 = set(norm2.split())

    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    return len(intersection) / len(union) if union else 0.0
