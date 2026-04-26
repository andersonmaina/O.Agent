"""
OLLAMA-AGENT Tools Package
Tools are loaded lazily via core.registry.load_tools_from_directory().
Do NOT add wildcard imports here — they cause all modules to be
imported eagerly and will break startup if any tool has a bad docstring.
"""

__version__ = "1.0.0"
__author__ = "PyTools Team"
