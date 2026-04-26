"""
File manipulation and management utilities
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from smolagents import tool


def _safe_path(path_str: str) -> Path:
    """Ensure path is within the current working directory."""
    try:
        p = Path(path_str).resolve()
        cwd = Path.cwd().resolve()
        # Verify that the path is inside the CWD
        p.relative_to(cwd)
        return p
    except ValueError:
        # If relative_to fails, it means it's outside
        raise PermissionError(f"Access denied: path '{path_str}' is outside the working directory.")


@tool
def read_file_tool(path: str, encoding: str = 'utf-8') -> str:
    """Read and return contents of a local file.
    Args:
        path: Relative path to the file.
        encoding: Text encoding (default 'utf-8').
    """
    try:
        return _safe_path(path).read_text(encoding=encoding)
    except Exception as e:
        return f"Error reading file {path}: {e}"


@tool
def write_file_tool(path: str, content: str, encoding: str = 'utf-8', mode: str = 'write') -> str:
    """Write or overwrite content to a local file.
    Args:
        path: Relative path to the file.
        content: Text content to write.
        encoding: Text encoding (default 'utf-8').
        mode: 'write' (overwrite) or 'append'.
    """
    try:
        p = _safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        write_mode = 'w' if mode == 'write' else 'a'
        with open(p, write_mode, encoding=encoding) as f:
            f.write(content)
        return f"Successfully {'wrote' if mode == 'write' else 'appended'} to {path}"
    except Exception as e:
        return f"Error writing to file {path}: {e}"


@tool
def edit_file_tool(path: str, old_str: str, new_str: str) -> str:
    """Efficiently replace a specific string in a file with new content.
    Args:
        path: Relative path to the file.
        old_str: The exact string to find and replace.
        new_str: The replacement string.
    """
    try:
        p = _safe_path(path)
        if not p.exists():
            return f"Error: File {path} does not exist."
        
        content = p.read_text(encoding='utf-8')
        if old_str not in content:
            return f"Error: Could not find '{old_str}' in {path}."
        
        new_content = content.replace(old_str, new_str)
        p.write_text(new_content, encoding='utf-8')
        return f"Successfully updated {path}"
    except Exception as e:
        return f"Error editing file {path}: {e}"


@tool
def list_files_tool(directory: str = '.', pattern: str = '*') -> str:
    """List files in a directory matching a pattern.
    Args:
        directory: Relative directory path.
        pattern: Glob pattern (e.g. '*.py').
    """
    try:
        p = _safe_path(directory)
        files = [str(f.relative_to(Path.cwd())) for f in p.glob(pattern) if f.is_file()]
        if not files:
            return f"No files found in {directory} matching {pattern}"
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {e}"


@tool
def delete_file_tool(path: str) -> str:
    """Delete a local file.
    Args:
        path: Relative path to the file.
    """
    try:
        p = _safe_path(path)
        os.remove(p)
        return f"Deleted {path}"
    except Exception as e:
        return f"Error deleting file {path}: {e}"


@tool
def create_directory_tool(path: str) -> str:
    """Create a new directory.
    Args:
        path: Relative path for the new directory.
    """
    try:
        p = _safe_path(path)
        p.mkdir(parents=True, exist_ok=True)
        return f"Created directory: {path}"
    except Exception as e:
        return f"Error creating directory {path}: {e}"


def copy_file(source: str, destination: str) -> str:
    """Copy a file from source to destination."""
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return f"Copied {source} to {destination}"


def move_file(source: str, destination: str) -> str:
    """Move a file from source to destination."""
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source, destination)
    return f"Moved {source} to {destination}"


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(path)


def get_file_extension(path: str) -> str:
    """Get file extension without the dot."""
    return Path(path).suffix.lstrip('.')


def list_directories(directory: str = '.') -> list:
    """List all directories in a path."""
    return [str(d) for d in Path(directory).iterdir() if d.is_dir()]


def delete_directory(path: str, recursive: bool = False) -> str:
    """Delete a directory."""
    if recursive:
        shutil.rmtree(path)
    else:
        os.rmdir(path)
    return f"Deleted directory: {path}"


def get_directory_size(path: str) -> int:
    """Get total size of directory in bytes."""
    total = 0
    for entry in Path(path).rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total


def find_files(directory: str, pattern: str = '*', recursive: bool = True) -> list:
    """Find files matching pattern in directory."""
    if recursive:
        return [str(f) for f in Path(directory).rglob(pattern) if f.is_file()]
    return [str(f) for f in Path(directory).glob(pattern) if f.is_file()]


def backup_file(path: str, backup_dir: str = None) -> str:
    """Create a backup of a file with timestamp."""
    if backup_dir is None:
        backup_dir = os.path.dirname(path)
    
    filename = os.path.basename(path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{filename}.{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(path, backup_path)
    return backup_path


def get_file_hash(path: str, algorithm: str = 'sha256') -> str:
    """Calculate hash of a file."""
    hash_func = getattr(hashlib, algorithm)()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def get_file_info(path: str) -> dict:
    """Get detailed file information."""
    stat = os.stat(path)
    return {
        'name': os.path.basename(path),
        'path': os.path.abspath(path),
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': get_file_extension(path),
    }

