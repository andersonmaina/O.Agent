import importlib
import inspect
import os
import sys
from typing import List, Any
from smolagents import Tool


def is_potential_tool_file(filepath: str) -> bool:
    """Quickly check if a file might contain tools without importing it."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return "@tool" in content or "class " in content
    except Exception:
        return False


def load_module_tools(module_name: str) -> List[Any]:
    """Load tools from a single module, with verbose error reporting."""
    tools = []
    try:
        # Import or reload module
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)

        # Find all functions with the @tool attribute
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, "_is_tool") and obj._is_tool:
                tools.append(obj)
            elif inspect.isclass(obj) and issubclass(obj, Tool) and obj != Tool:
                try:
                    tools.append(obj())
                except Exception:
                    pass

    except Exception as e:
        # Print clearly so users know which tool file is broken
        print(f"    \033[1;33m[WARN] Skipped '{module_name}': {e}\033[0m")

    return tools


def load_tools_from_directory(directory: str) -> List[Any]:
    """
    Dynamically load tools from all Python files in a directory.
    Sequential loading is used for stability and clearer error output.
    """
    all_tools = []

    if not os.path.isabs(directory):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        directory = os.path.join(project_root, directory)

    if not os.path.exists(directory):
        print(f"    \033[1;31m[ERROR] Tools directory not found: {directory}\033[0m")
        return []

    # Collect candidate files
    potential_modules = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(directory, filename)
            if is_potential_tool_file(filepath):
                potential_modules.append(f"tools.{filename[:-3]}")

    # Load modules sequentially (safer than threads for Python imports)
    for module_name in potential_modules:
        module_tools = load_module_tools(module_name)
        all_tools.extend(module_tools)

    return all_tools
