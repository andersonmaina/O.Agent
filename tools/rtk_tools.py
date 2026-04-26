import os
import re
from smolagents import tool

@tool
def rtk_read_file(path: str, mode: str = "balanced") -> str:
    """Reads a file with token-optimized filtering (RTK Logic).
    
    Args:
        path: Relative path to the file.
        mode: 'minimal' (remove comments), 'balanced' (remove comments & empty lines), 
              'aggressive' (only keep signatures/declarations).
    """
    try:
        if not os.path.exists(path):
            return f"Error: File {path} not found"
            
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        filtered = []
        for line in lines:
            line_strip = line.strip()
            
            # Basic comment removal (Python/JS/C Style)
            if mode in ["minimal", "balanced", "aggressive"]:
                if line_strip.startswith(('#', '//', '/*', '*')):
                    continue
            
            # Empty line removal
            if mode in ["balanced", "aggressive"]:
                if not line_strip:
                    continue
            
            # Aggressive: only keep structural signatures
            if mode == "aggressive":
                if not any(keyword in line_strip for keyword in ["def ", "class ", "interface ", "function ", "struct ", "type "]):
                    continue
                    
            filtered.append(line)
            
        content = "".join(filtered)
        tokens = len(content) // 4
        return f"[RTK {mode.upper()}] ({tokens} tokens):\n\n{content}"
        
    except Exception as e:
        return f"Error: {e}"

@tool
def rtk_ls(directory: str = ".", depth: int = 2) -> str:
    """Token-optimized directory tree listing.
    
    Args:
        directory: Directory to list.
        depth: Maximum depth to recurse.
    """
    ignore_list = [".git", "node_modules", "__pycache__", "venv", ".idea", ".vscode", "tmp_rtk"]
    
    def _tree(path, current_depth):
        if current_depth > depth: return ""
        try:
            items = os.listdir(path)
        except: return ""
        
        output = ""
        for item in sorted(items):
            if item in ignore_list: continue
            full_path = os.path.join(path, item)
            indent = "  " * current_depth
            if os.path.isdir(full_path):
                output += f"{indent}📂 {item}/\n"
                output += _tree(full_path, current_depth + 1)
            else:
                output += f"{indent}📄 {item}\n"
        return output

    result = _tree(directory, 0)
    return f"[RTK LS] Optimized Tree:\n\n{result}"
