"""
File manipulation and management utilities
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime


def read_file(path: str, encoding: str = 'utf-8') -> str:
    """Read and return contents of a file."""
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def write_file(path: str, content: str, encoding: str = 'utf-8', mode: str = 'write') -> str:
    """Write content to a file. Creates parent directories if needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    write_mode = 'w' if mode == 'write' else 'a'
    with open(path, write_mode, encoding=encoding) as f:
        f.write(content)
    return f"Successfully wrote to {path}"


def append_file(path: str, content: str, encoding: str = 'utf-8') -> str:
    """Append content to a file."""
    return write_file(path, content, encoding, mode='append')


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


def delete_file(path: str) -> str:
    """Delete a file."""
    os.remove(path)
    return f"Deleted {path}"


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(path)


def get_file_extension(path: str) -> str:
    """Get file extension without the dot."""
    return Path(path).suffix.lstrip('.')


def list_files(directory: str = '.', pattern: str = '*') -> list:
    """List all files in a directory matching pattern."""
    return [str(f) for f in Path(directory).glob(pattern) if f.is_file()]


def list_directories(directory: str = '.') -> list:
    """List all directories in a path."""
    return [str(d) for d in Path(directory).iterdir() if d.is_dir()]


def create_directory(path: str) -> str:
    """Create a directory and all parent directories."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return f"Created directory: {path}"


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
