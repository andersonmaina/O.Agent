"""
System utilities and OS interaction tools
"""

import os
import sys
import platform
import subprocess
import shutil
from typing import Dict, List, Optional


def get_system_info() -> Dict[str, str]:
    """Get basic system information."""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }


def get_platform_info() -> str:
    """Get detailed platform information."""
    return f"{platform.system()} {platform.release()} ({platform.machine()})"


def get_cpu_count() -> int:
    """Get number of CPU cores."""
    return os.cpu_count() or 1


def get_memory_usage() -> Dict[str, int]:
    """Get memory usage information."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
        }
    except ImportError:
        # Fallback for systems without psutil
        if platform.system() == 'Linux':
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            mem_info = {}
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    mem_info[parts[0].rstrip(':')] = int(parts[1])
            return {
                'total': mem_info.get('MemTotal', 0) * 1024,
                'available': mem_info.get('MemAvailable', 0) * 1024,
            }
        return {'error': 'psutil not available'}


def get_disk_usage(path: str = '/') -> Dict[str, int]:
    """Get disk usage information for a path."""
    try:
        import psutil
        usage = psutil.disk_usage(path)
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent,
        }
    except ImportError:
        total, used, free = shutil.disk_usage(path)
        return {
            'total': total,
            'used': used,
            'free': free,
            'percent': (used / total) * 100,
        }


def get_environment_variables() -> Dict[str, str]:
    """Get all environment variables."""
    return dict(os.environ)


def get_environment_variable(name: str, default: str = None) -> Optional[str]:
    """Get a specific environment variable."""
    return os.environ.get(name, default)


def run_command(command: str, shell: bool = True, timeout: int = 30) -> Dict[str, any]:
    """Run a shell command and return results."""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': f'Command timed out after {timeout}s',
            'success': False,
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False,
        }


def is_admin() -> bool:
    """Check if running with admin/root privileges."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False


def get_current_directory() -> str:
    """Get current working directory."""
    return os.getcwd()


def change_directory(path: str) -> str:
    """Change current working directory."""
    os.chdir(path)
    return os.getcwd()


def get_home_directory() -> str:
    """Get user home directory."""
    return os.path.expanduser('~')


def get_temp_directory() -> str:
    """Get system temp directory."""
    return tempfile.gettempdir()


def list_processes() -> List[Dict]:
    """List running processes (requires psutil)."""
    try:
        import psutil
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    except ImportError:
        return [{'error': 'psutil not available'}]


def get_username() -> str:
    """Get current username."""
    return os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USERNAME', 'unknown')


def shutdown_system(delay: int = 0) -> str:
    """Shutdown system (requires admin)."""
    if platform.system() == 'Windows':
        cmd = f'shutdown /s /t {delay}'
    else:
        cmd = f'sudo shutdown -h +{delay // 60}'
    return f"Would execute: {cmd} (blocked for safety)"


def restart_system(delay: int = 0) -> str:
    """Restart system (requires admin)."""
    if platform.system() == 'Windows':
        cmd = f'shutdown /r /t {delay}'
    else:
        cmd = f'sudo reboot'
    return f"Would execute: {cmd} (blocked for safety)"


import tempfile
