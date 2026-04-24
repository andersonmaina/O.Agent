"""
Chat Memory Management System
Persistent storage for conversations, chats, and task history
"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from uuid import uuid4


@dataclass
class Message:
    """A single message in a chat conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Task:
    """A task within a chat session."""
    id: str
    title: str
    input: str
    output: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    created_at: str
    completed_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Chat:
    """A chat session containing messages and tasks."""
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message]
    tasks: List[Task]
    metadata: Optional[Dict[str, Any]] = None


class ChatMemoryManager:
    """Manages persistent chat memory with file-based storage."""

    def __init__(self, storage_dir: str = None):
        """Initialize the chat memory manager."""
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chat_storage')

        self.storage_dir = Path(storage_dir)
        self.chats_dir = self.storage_dir / 'chats'
        self.index_file = self.storage_dir / 'chat_index.json'

        self._ensure_storage_exists()
        self._load_index()

    def _ensure_storage_exists(self):
        """Create storage directories if they don't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.chats_dir.mkdir(parents=True, exist_ok=True)

    def _load_index(self):
        """Load the chat index from disk."""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self._index = json.load(f)
        else:
            self._index = {'chats': {}, 'active_chat': None}
            self._save_index()

    def _save_index(self):
        """Save the chat index to disk."""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self._index, f, indent=2)

    def _get_chat_path(self, chat_id: str) -> Path:
        """Get the file path for a chat."""
        return self.chats_dir / f"{chat_id}.json"

    def _save_chat(self, chat: Chat):
        """Save a chat to disk."""
        chat_path = self._get_chat_path(chat.id)
        with open(chat_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(chat), f, indent=2, default=str)

        self._index['chats'][chat.id] = {
            'title': chat.title,
            'created_at': chat.created_at,
            'updated_at': chat.updated_at,
            'task_count': len(chat.tasks),
            'message_count': len(chat.messages)
        }
        self._save_index()

    def _load_chat(self, chat_id: str) -> Optional[Chat]:
        """Load a chat from disk."""
        chat_path = self._get_chat_path(chat_id)

        if not chat_path.exists():
            return None

        with open(chat_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return Chat(
            id=data['id'],
            title=data['title'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            messages=[Message(**m) if isinstance(m, dict) else m for m in data.get('messages', [])],
            tasks=[Task(**t) if isinstance(t, dict) else t for t in data.get('tasks', [])],
            metadata=data.get('metadata')
        )

    def create_chat(self, title: str = None) -> Chat:
        """Create a new chat session."""
        chat_id = str(uuid4())[:8]
        now = datetime.now().isoformat()

        chat = Chat(
            id=chat_id,
            title=title or f"Chat {chat_id}",
            created_at=now,
            updated_at=now,
            messages=[],
            tasks=[]
        )

        self._save_chat(chat)

        if self._index['active_chat'] is None:
            self._index['active_chat'] = chat_id
            self._save_index()

        return chat

    def get_chat(self, chat_id: str) -> Optional[Chat]:
        """Get a chat by ID."""
        return self._load_chat(chat_id)

    def list_chats(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List all chats, sorted by last updated."""
        chats = []

        for chat_id, info in self._index['chats'].items():
            chats.append({
                'id': chat_id,
                'title': info['title'],
                'created_at': info['created_at'],
                'updated_at': info['updated_at'],
                'task_count': info['task_count'],
                'message_count': info['message_count']
            })

        chats.sort(key=lambda x: x['updated_at'], reverse=True)
        return chats[:limit]

    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat session."""
        chat_path = self._get_chat_path(chat_id)

        if not chat_path.exists():
            return False

        chat_path.unlink()

        if chat_id in self._index['chats']:
            del self._index['chats'][chat_id]

        if self._index['active_chat'] == chat_id:
            remaining = list(self._index['chats'].keys())
            self._index['active_chat'] = remaining[0] if remaining else None

        self._save_index()
        return True

    def set_active_chat(self, chat_id: str) -> bool:
        """Set the active chat session."""
        if chat_id not in self._index['chats']:
            return False

        self._index['active_chat'] = chat_id
        self._save_index()
        return True

    def get_active_chat(self) -> Optional[Chat]:
        """Get the currently active chat."""
        active_id = self._index.get('active_chat')

        if not active_id:
            return None

        return self._load_chat(active_id)

    def get_or_create_active_chat(self) -> Chat:
        """Get active chat or create one if none exists."""
        chat = self.get_active_chat()

        if chat:
            return chat

        return self.create_chat()

    def add_message(self, chat_id: str, role: str, content: str,
                    metadata: Dict[str, Any] = None) -> Message:
        """Add a message to a chat."""
        chat = self._load_chat(chat_id)

        if not chat:
            raise ValueError(f"Chat {chat_id} not found")

        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata
        )

        chat.messages.append(message)
        chat.updated_at = datetime.now().isoformat()

        self._save_chat(chat)
        return message

    def get_messages(self, chat_id: str, limit: int = 50) -> List[Message]:
        """Get messages from a chat."""
        chat = self._load_chat(chat_id)

        if not chat:
            return []

        return chat.messages[-limit:]

    def create_task(self, chat_id: str, title: str, input_text: str) -> Task:
        """Create a new task within a chat."""
        chat = self._load_chat(chat_id)

        if not chat:
            raise ValueError(f"Chat {chat_id} not found")

        task = Task(
            id=str(uuid4())[:6],
            title=title,
            input=input_text,
            output="",
            status="pending",
            created_at=datetime.now().isoformat()
        )

        chat.tasks.append(task)
        chat.updated_at = datetime.now().isoformat()

        self._save_chat(chat)
        return task

    def update_task(self, chat_id: str, task_id: str,
                    output: str = None, status: str = None) -> Optional[Task]:
        """Update a task's status and output."""
        chat = self._load_chat(chat_id)

        if not chat:
            return None

        for task in chat.tasks:
            if task.id == task_id:
                if output is not None:
                    task.output = output
                if status is not None:
                    task.status = status
                    if status in ['completed', 'failed']:
                        task.completed_at = datetime.now().isoformat()

                chat.updated_at = datetime.now().isoformat()
                self._save_chat(chat)
                return task

        return None

    def get_task(self, chat_id: str, task_id: str) -> Optional[Task]:
        """Get a specific task from a chat."""
        chat = self._load_chat(chat_id)

        if not chat:
            return None

        for task in chat.tasks:
            if task.id == task_id:
                return task

        return None

    def get_tasks(self, chat_id: str, status: str = None) -> List[Task]:
        """Get all tasks from a chat, optionally filtered by status."""
        chat = self._load_chat(chat_id)

        if not chat:
            return []

        if status:
            return [t for t in chat.tasks if t.status == status]

        return chat.tasks

    def get_chat_history(self, chat_id: str, include_tasks: bool = True) -> Dict[str, Any]:
        """Get complete chat history."""
        chat = self._load_chat(chat_id)

        if not chat:
            return {}

        result = {
            'id': chat.id,
            'title': chat.title,
            'created_at': chat.created_at,
            'updated_at': chat.updated_at,
            'messages': [asdict(m) for m in chat.messages],
            'metadata': chat.metadata
        }

        if include_tasks:
            result['tasks'] = [asdict(t) for t in chat.tasks]

        return result

    def export_chat(self, chat_id: str, output_path: str) -> str:
        """Export a chat to a file."""
        chat = self._load_chat(chat_id)

        if not chat:
            raise ValueError(f"Chat {chat_id} not found")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(chat), f, indent=2, default=str)

        return f"Chat exported to {output_path}"

    def import_chat(self, input_path: str) -> Chat:
        """Import a chat from a file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        chat = Chat(**data)
        chat.id = str(uuid4())[:8]

        self._save_chat(chat)
        return chat

    def search_chats(self, query: str) -> List[Dict[str, Any]]:
        """Search across all chats for a query string."""
        results = []
        query_lower = query.lower()

        for chat_id in self._index['chats'].keys():
            chat = self._load_chat(chat_id)

            if not chat:
                continue

            matches = []

            for i, msg in enumerate(chat.messages):
                if query_lower in msg.content.lower():
                    matches.append({
                        'type': 'message',
                        'index': i,
                        'content': msg.content[:200]
                    })

            for task in chat.tasks:
                if query_lower in task.input.lower() or query_lower in task.output.lower():
                    matches.append({
                        'type': 'task',
                        'task_id': task.id,
                        'title': task.title
                    })

            if matches:
                results.append({
                    'chat_id': chat_id,
                    'chat_title': chat.title,
                    'matches': matches
                })

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about chat storage."""
        total_messages = 0
        total_tasks = 0
        total_size = 0

        for chat_path in self.chats_dir.glob('*.json'):
            total_size += chat_path.stat().st_size

            with open(chat_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_messages += len(data.get('messages', []))
                total_tasks += len(data.get('tasks', []))

        return {
            'total_chats': len(self._index['chats']),
            'total_messages': total_messages,
            'total_tasks': total_tasks,
            'storage_size_bytes': total_size,
            'active_chat': self._index.get('active_chat'),
            'storage_path': str(self.storage_dir)
        }

    def clear_all(self) -> str:
        """Clear all chat data."""
        for chat_path in self.chats_dir.glob('*.json'):
            chat_path.unlink()

        self._index = {'chats': {}, 'active_chat': None}
        self._save_index()

        return "All chat data cleared"


# Global instance for convenience
_chat_memory = None


def get_chat_memory() -> ChatMemoryManager:
    """Get the global chat memory manager instance."""
    global _chat_memory
    if _chat_memory is None:
        _chat_memory = ChatMemoryManager()
    return _chat_memory
