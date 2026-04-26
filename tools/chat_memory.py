"""
Chat Memory Management System - SQLite Edition
Persistent storage for conversations, chats, and task history using SQLite
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from uuid import uuid4
from smolagents import tool


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
    """Manages persistent chat memory with SQLite backend."""

    def __init__(self, storage_dir: str = None):
        """Initialize the chat memory manager."""
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chat_storage')

        self.storage_dir = Path(storage_dir)
        self.db_path = self.storage_dir / 'chat_memory.db'
        
        self._ensure_storage_exists()
        self._init_db()
        
        # Check if migration is needed
        self._migrate_from_json()

    def _ensure_storage_exists(self):
        """Create storage directories if they don't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize the SQLite database schema."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    metadata TEXT,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    chat_id TEXT,
                    title TEXT,
                    input TEXT,
                    output TEXT,
                    status TEXT,
                    created_at TEXT,
                    completed_at TEXT,
                    metadata TEXT,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)
            conn.commit()

    def _migrate_from_json(self):
        """Migrate data from old JSON files to SQLite if they exist."""
        index_file = self.storage_dir / 'chat_index.json'
        chats_dir = self.storage_dir / 'chats'
        
        if not index_file.exists():
            return

        print("Migrating chat memory to SQLite...")
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            active_chat = index_data.get('active_chat')
            if active_chat:
                self.set_active_chat(active_chat)

            for chat_id in index_data.get('chats', {}).keys():
                chat_file = chats_dir / f"{chat_id}.json"
                if chat_file.exists():
                    with open(chat_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Insert chat
                    with self._get_connection() as conn:
                        conn.execute(
                            "INSERT OR IGNORE INTO chats (id, title, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?)",
                            (data['id'], data['title'], data['created_at'], data['updated_at'], json.dumps(data.get('metadata')))
                        )
                        
                        # Insert messages
                        for m in data.get('messages', []):
                            conn.execute(
                                "INSERT INTO messages (chat_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                                (data['id'], m['role'], m['content'], m['timestamp'], json.dumps(m.get('metadata')))
                            )
                        
                        # Insert tasks
                        for t in data.get('tasks', []):
                            conn.execute(
                                "INSERT OR IGNORE INTO tasks (id, chat_id, title, input, output, status, created_at, completed_at, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (t['id'], data['id'], t['title'], t['input'], t.get('output', ''), t['status'], t['created_at'], t.get('completed_at'), json.dumps(t.get('metadata')))
                            )
                        conn.commit()
            
            # Archive old files
            archive_dir = self.storage_dir / 'archived_json'
            archive_dir.mkdir(exist_ok=True)
            if index_file.exists():
                os.rename(index_file, archive_dir / 'chat_index.json')
            if chats_dir.exists():
                shutil_move_alternative(chats_dir, archive_dir / 'chats')
                
            print("Migration complete.")
        except Exception as e:
            print(f"Migration error: {e}")

    def create_chat(self, title: str = None) -> Chat:
        chat_id = str(uuid4())[:8]
        now = datetime.now().isoformat()
        title = title or f"Chat {chat_id}"

        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO chats (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (chat_id, title, now, now)
            )
            conn.commit()

        # Set as active if none exists
        if not self.get_active_chat():
            self.set_active_chat(chat_id)

        return Chat(id=chat_id, title=title, created_at=now, updated_at=now, messages=[], tasks=[])

    def get_chat(self, chat_id: str) -> Optional[Chat]:
        with self._get_connection() as conn:
            chat_row = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
            if not chat_row:
                return None
            
            messages = []
            for m_row in conn.execute("SELECT * FROM messages WHERE chat_id = ?", (chat_id,)).fetchall():
                messages.append(Message(
                    role=m_row['role'],
                    content=m_row['content'],
                    timestamp=m_row['timestamp'],
                    metadata=json.loads(m_row['metadata']) if m_row['metadata'] else None
                ))
            
            tasks = []
            for t_row in conn.execute("SELECT * FROM tasks WHERE chat_id = ?", (chat_id,)).fetchall():
                tasks.append(Task(
                    id=t_row['id'],
                    title=t_row['title'],
                    input=t_row['input'],
                    output=t_row['output'],
                    status=t_row['status'],
                    created_at=t_row['created_at'],
                    completed_at=t_row['completed_at'],
                    metadata=json.loads(t_row['metadata']) if t_row['metadata'] else None
                ))
            
            return Chat(
                id=chat_row['id'],
                title=chat_row['title'],
                created_at=chat_row['created_at'],
                updated_at=chat_row['updated_at'],
                messages=messages,
                tasks=tasks,
                metadata=json.loads(chat_row['metadata']) if chat_row['metadata'] else None
            )

    def list_chats(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT c.id, c.title, c.created_at, c.updated_at,
                       (SELECT COUNT(*) FROM messages WHERE chat_id = c.id) as message_count,
                       (SELECT COUNT(*) FROM tasks WHERE chat_id = c.id) as task_count
                FROM chats c
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            return [dict(row) for row in rows]

    def delete_chat(self, chat_id: str) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            conn.commit()
            
            # Reset active chat if deleted
            active = self.get_active_chat()
            if active and active.id == chat_id:
                remaining = self.list_chats(1)
                if remaining:
                    self.set_active_chat(remaining[0]['id'])
                else:
                    conn.execute("DELETE FROM settings WHERE key = 'active_chat'")
                    conn.commit()
            return True

    def set_active_chat(self, chat_id: str) -> bool:
        with self._get_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('active_chat', ?)", (chat_id,))
            conn.commit()
            return True

    def get_active_chat(self) -> Optional[Chat]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = 'active_chat'").fetchone()
            if not row:
                return None
            return self.get_chat(row['value'])

    def get_or_create_active_chat(self) -> Chat:
        chat = self.get_active_chat()
        return chat if chat else self.create_chat()

    def add_message(self, chat_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> Message:
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (chat_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (chat_id, role, content, now, json.dumps(metadata) if metadata else None)
            )
            conn.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
            conn.commit()
        return Message(role=role, content=content, timestamp=now, metadata=metadata)

    def get_messages(self, chat_id: str, limit: int = 50) -> List[Message]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (chat_id, limit)
            ).fetchall()
            
            messages = []
            for row in reversed(rows):
                messages.append(Message(
                    role=row['role'],
                    content=row['content'],
                    timestamp=row['timestamp'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                ))
            return messages

    def create_task(self, chat_id: str, title: str, input_text: str) -> Task:
        task_id = str(uuid4())[:6]
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks (id, chat_id, title, input, output, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (task_id, chat_id, title, input_text, "", "pending", now)
            )
            conn.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
            conn.commit()
        
        return Task(id=task_id, title=title, input=input_text, output="", status="pending", created_at=now)

    def update_task(self, chat_id: str, task_id: str, output: str = None, status: str = None) -> Optional[Task]:
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            if output is not None and status in ['completed', 'failed']:
                conn.execute(
                    "UPDATE tasks SET output = ?, status = ?, completed_at = ? WHERE id = ?",
                    (output, status, now, task_id)
                )
            elif output is not None:
                conn.execute("UPDATE tasks SET output = ? WHERE id = ?", (output, task_id))
            elif status is not None:
                conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
                
            conn.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
            conn.commit()
        return self.get_task(chat_id, task_id)

    def get_task(self, chat_id: str, task_id: str) -> Optional[Task]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not row: return None
            return Task(
                id=row['id'], title=row['title'], input=row['input'],
                output=row['output'], status=row['status'],
                created_at=row['created_at'], completed_at=row['completed_at'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            )

    def get_tasks(self, chat_id: str, status: str = None) -> List[Task]:
        with self._get_connection() as conn:
            query = "SELECT * FROM tasks WHERE chat_id = ?"
            params = [chat_id]
            if status:
                query += " AND status = ?"
                params.append(status)
            
            rows = conn.execute(query, params).fetchall()
            return [Task(
                id=row['id'], title=row['title'], input=row['input'],
                output=row['output'], status=row['status'],
                created_at=row['created_at'], completed_at=row['completed_at'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            ) for row in rows]

    def search_chats(self, query: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query_param = f"%{query}%"
            # Search messages
            msg_rows = conn.execute("""
                SELECT DISTINCT c.id as chat_id, c.title as chat_title, 'message' as type
                FROM chats c JOIN messages m ON c.id = m.chat_id
                WHERE m.content LIKE ?
            """, (query_param,)).fetchall()
            
            # Search tasks
            task_rows = conn.execute("""
                SELECT DISTINCT c.id as chat_id, c.title as chat_title, 'task' as type
                FROM chats c JOIN tasks t ON c.id = t.chat_id
                WHERE t.input LIKE ? OR t.output LIKE ? OR t.title LIKE ?
            """, (query_param, query_param, query_param)).fetchall()
            
            # Combine
            results = {}
            for row in list(msg_rows) + list(task_rows):
                cid = row['chat_id']
                if cid not in results:
                    results[cid] = {'chat_id': cid, 'chat_title': row['chat_title'], 'matches': []}
                results[cid]['matches'].append({'type': row['type']})
                
            return list(results.values())

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_chats = conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
            total_messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            
            return {
                'total_chats': total_chats,
                'total_messages': total_messages,
                'total_tasks': total_tasks,
                'storage_size_bytes': os.path.getsize(self.db_path),
                'active_chat': (self.get_active_chat().id if self.get_active_chat() else None),
                'storage_path': str(self.db_path)
            }

    def clear_all(self) -> str:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM tasks")
            conn.execute("DELETE FROM chats")
            conn.execute("DELETE FROM settings")
            conn.commit()
        return "All chat data cleared"

def shutil_move_alternative(src, dst):
    import shutil
    try:
        shutil.move(str(src), str(dst))
    except:
        pass

# Global instance for convenience
_chat_memory = None

def get_chat_memory() -> ChatMemoryManager:
    global _chat_memory
    if _chat_memory is None:
        _chat_memory = ChatMemoryManager()
    return _chat_memory

# ── Agent Tools ──────────────────────────────────────────────
@tool
def chat_list_tool(limit: int = 20) -> str:
    """List all chat sessions.

    Args:
        limit: Maximum number of chats to return.
    """
    chats = get_chat_memory().list_chats(limit)
    if not chats: return "No chats found."
    lines = ["Saved Chats:"]
    for c in chats:
        lines.append(f"- [{c['id']}] {c['title']} ({c['message_count']} msgs, {c['task_count']} tasks)")
    return "\n".join(lines)

@tool
def chat_create_tool(title: str = None) -> str:
    """Create a new chat session.

    Args:
        title: Optional title for the new chat session.
    """
    chat = get_chat_memory().create_chat(title)
    return f"Created chat: [{chat.id}] {chat.title}"

@tool
def chat_switch_tool(chat_id: str) -> str:
    """Switch the active chat context.

    Args:
        chat_id: The ID of the chat session to switch to.
    """
    if get_chat_memory().set_active_chat(chat_id):
        return f"Switched to chat: {chat_id}"
    return f"Chat {chat_id} not found."

@tool
def chat_delete_tool(chat_id: str) -> str:
    """Delete a chat session.

    Args:
        chat_id: The ID of the chat session to delete.
    """
    if get_chat_memory().delete_chat(chat_id):
        return f"Deleted chat: {chat_id}"
    return f"Chat {chat_id} not found."

@tool
def chat_history_tool(chat_id: str = None, limit: int = 20) -> str:
    """View message history for a chat.

    Args:
        chat_id: Chat ID to view history for (defaults to active chat).
        limit: Maximum number of messages to retrieve.
    """
    memory = get_chat_memory()
    if not chat_id:
        active = memory.get_active_chat()
        if not active: return "No active chat."
        chat_id = active.id
    
    messages = memory.get_messages(chat_id, limit)
    if not messages: return "No history."
    
    lines = [f"History for {chat_id}:"]
    for m in messages:
        lines.append(f"[{m.timestamp[:16]}] {m.role.upper()}: {m.content[:100]}...")
    return "\n".join(lines)

@tool
def task_list_tool(chat_id: str = None, status: str = None) -> str:
    """List tasks in a chat.

    Args:
        chat_id: Chat ID to list tasks for (defaults to active chat).
        status: Optional status filter ('pending', 'in_progress', 'completed', 'failed').
    """
    memory = get_chat_memory()
    if not chat_id:
        active = memory.get_active_chat()
        if not active: return "No active chat."
        chat_id = active.id
    
    tasks = memory.get_tasks(chat_id, status)
    if not tasks: return "No tasks found."
    lines = [f"Tasks for {chat_id}:"]
    for t in tasks:
        lines.append(f"- [{t.id}] {t.title} ({t.status})")
    return "\n".join(lines)
