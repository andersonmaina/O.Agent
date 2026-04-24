"""
Power user tools - utilities for enhanced productivity
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime


def user_profile_create(name: str, email: str = None, preferences: Dict = None) -> str:
    """Create a user profile.
    Args:
        name: user name.
        email: user email (optional).
        preferences: user preferences dict (optional).
    """
    profile = {
        'name': name,
        'email': email,
        'preferences': preferences or {},
        'created_at': datetime.now().isoformat()
    }
    profile_path = os.path.join('.agent_data', 'user_profile.json')
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    return f"User profile created for {name}"


def user_profile_get() -> str:
    """Get current user profile."""
    profile_path = os.path.join('.agent_data', 'user_profile.json')
    if not os.path.exists(profile_path):
        return "No user profile found"
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    return json.dumps(profile, indent=2)


def user_preferences_set(key: str, value: str) -> str:
    """Set a user preference.
    Args:
        key: preference key.
        value: preference value.
    """
    profile_path = os.path.join('.agent_data', 'user_profile.json')
    if not os.path.exists(profile_path):
        return "No user profile found. Create one first."
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    profile['preferences'][key] = value
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    return f"Preference '{key}' set to '{value}'"


def user_preferences_get(key: str = None) -> str:
    """Get user preferences.
    Args:
        key: specific preference key (optional).
    """
    profile_path = os.path.join('.agent_data', 'user_profile.json')
    if not os.path.exists(profile_path):
        return "No user profile found"
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    prefs = profile.get('preferences', {})
    if key:
        return f"{key}: {prefs.get(key, 'not set')}"
    return json.dumps(prefs, indent=2)


def user_bookmark_add(name: str, url: str, tags: List[str] = None) -> str:
    """Add a bookmark.
    Args:
        name: bookmark name.
        url: bookmark URL.
        tags: list of tags (optional).
    """
    bookmarks_path = os.path.join('.agent_data', 'bookmarks.json')
    bookmarks = []
    if os.path.exists(bookmarks_path):
        with open(bookmarks_path, 'r') as f:
            bookmarks = json.load(f)
    bookmark = {
        'name': name,
        'url': url,
        'tags': tags or [],
        'created_at': datetime.now().isoformat()
    }
    bookmarks.append(bookmark)
    os.makedirs(os.path.dirname(bookmarks_path), exist_ok=True)
    with open(bookmarks_path, 'w') as f:
        json.dump(bookmarks, f, indent=2)
    return f"Bookmark '{name}' added"


def user_bookmarks_list(tag: str = None) -> str:
    """List all bookmarks.
    Args:
        tag: filter by tag (optional).
    """
    bookmarks_path = os.path.join('.agent_data', 'bookmarks.json')
    if not os.path.exists(bookmarks_path):
        return "No bookmarks found"
    with open(bookmarks_path, 'r') as f:
        bookmarks = json.load(f)
    if tag:
        bookmarks = [b for b in bookmarks if tag in b.get('tags', [])]
    if not bookmarks:
        return "No bookmarks found"
    return json.dumps(bookmarks, indent=2)


def user_notes_add(title: str, content: str, tags: List[str] = None) -> str:
    """Add a note.
    Args:
        title: note title.
        content: note content.
        tags: list of tags (optional).
    """
    notes_path = os.path.join('.agent_data', 'notes.json')
    notes = []
    if os.path.exists(notes_path):
        with open(notes_path, 'r') as f:
            notes = json.load(f)
    note = {
        'title': title,
        'content': content,
        'tags': tags or [],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    notes.append(note)
    os.makedirs(os.path.dirname(notes_path), exist_ok=True)
    with open(notes_path, 'w') as f:
        json.dump(notes, f, indent=2)
    return f"Note '{title}' added"


def user_notes_list(search: str = None) -> str:
    """List all notes.
    Args:
        search: search term in title/content (optional).
    """
    notes_path = os.path.join('.agent_data', 'notes.json')
    if not os.path.exists(notes_path):
        return "No notes found"
    with open(notes_path, 'r') as f:
        notes = json.load(f)
    if search:
        search_lower = search.lower()
        notes = [n for n in notes 
                 if search_lower in n['title'].lower() 
                 or search_lower in n['content'].lower()]
    if not notes:
        return "No notes found"
    return json.dumps(notes, indent=2)


def user_history_add(action: str, details: str = None) -> str:
    """Add an action to user history.
    Args:
        action: action name.
        details: action details (optional).
    """
    history_path = os.path.join('.agent_data', 'history.json')
    history = []
    if os.path.exists(history_path):
        with open(history_path, 'r') as f:
            history = json.load(f)
    entry = {
        'action': action,
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
    history.append(entry)
    # Keep only last 100 entries
    history = history[-100:]
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    return f"Action '{action}' recorded"


def user_history_list(limit: int = 10) -> str:
    """List recent user history.
    Args:
        limit: number of entries (default 10).
    """
    history_path = os.path.join('.agent_data', 'history.json')
    if not os.path.exists(history_path):
        return "No history found"
    with open(history_path, 'r') as f:
        history = json.load(f)
    return json.dumps(history[-limit:], indent=2)


def user_settings_get(category: str = None) -> str:
    """Get user settings.
    Args:
        category: settings category (optional).
    """
    settings_path = os.path.join('.agent_data', 'settings.json')
    if not os.path.exists(settings_path):
        return "No settings found"
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    if category:
        return json.dumps(settings.get(category, {}), indent=2)
    return json.dumps(settings, indent=2)


def user_settings_set(category: str, key: str, value: str) -> str:
    """Set a user setting.
    Args:
        category: settings category.
        key: setting key.
        value: setting value.
    """
    settings_path = os.path.join('.agent_data', 'settings.json')
    settings = {}
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    if category not in settings:
        settings[category] = {}
    settings[category][key] = value
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    return f"Setting '{category}.{key}' set to '{value}'"


def user_quick_action(name: str, command: str) -> str:
    """Create a quick action alias.
    Args:
        name: action name (alias).
        command: command to execute.
    """
    actions_path = os.path.join('.agent_data', 'quick_actions.json')
    actions = {}
    if os.path.exists(actions_path):
        with open(actions_path, 'r') as f:
            actions = json.load(f)
    actions[name] = {
        'command': command,
        'created_at': datetime.now().isoformat()
    }
    os.makedirs(os.path.dirname(actions_path), exist_ok=True)
    with open(actions_path, 'w') as f:
        json.dump(actions, f, indent=2)
    return f"Quick action '{name}' created"


def user_quick_actions_list() -> str:
    """List all quick actions."""
    actions_path = os.path.join('.agent_data', 'quick_actions.json')
    if not os.path.exists(actions_path):
        return "No quick actions found"
    with open(actions_path, 'r') as f:
        actions = json.load(f)
    return json.dumps(actions, indent=2)


def user_dashboard() -> str:
    """Get user dashboard summary."""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'profile': 'not set',
        'bookmarks': 0,
        'notes': 0,
        'history_entries': 0,
    }
    
    profile_path = os.path.join('.agent_data', 'user_profile.json')
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            profile = json.load(f)
            summary['profile'] = profile.get('name', 'unknown')
    
    bookmarks_path = os.path.join('.agent_data', 'bookmarks.json')
    if os.path.exists(bookmarks_path):
        with open(bookmarks_path, 'r') as f:
            summary['bookmarks'] = len(json.load(f))
    
    notes_path = os.path.join('.agent_data', 'notes.json')
    if os.path.exists(notes_path):
        with open(notes_path, 'r') as f:
            summary['notes'] = len(json.load(f))
    
    history_path = os.path.join('.agent_data', 'history.json')
    if os.path.exists(history_path):
        with open(history_path, 'r') as f:
            summary['history_entries'] = len(json.load(f))
    
    return json.dumps(summary, indent=2)
