"""
Agent-specific utilities and power tools for autonomous agents
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime


class AgentMemory:
    """Simple in-memory storage for agent context."""
    
    def __init__(self):
        self._storage = {}
        self._history = []
    
    def set(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        self._storage[key] = value
        self._history.append({
            'action': 'set',
            'key': key,
            'timestamp': datetime.now().isoformat()
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from memory."""
        return self._storage.get(key, default)
    
    def delete(self, key: str) -> bool:
        """Delete a key from memory."""
        if key in self._storage:
            del self._storage[key]
            self._history.append({
                'action': 'delete',
                'key': key,
                'timestamp': datetime.now().isoformat()
            })
            return True
        return False
    
    def clear(self) -> None:
        """Clear all memory."""
        self._storage.clear()
        self._history.append({
            'action': 'clear',
            'timestamp': datetime.now().isoformat()
        })
    
    def keys(self) -> List[str]:
        """Get all keys."""
        return list(self._storage.keys())
    
    def to_dict(self) -> Dict:
        """Export memory as dictionary."""
        return self._storage.copy()
    
    def history(self, limit: int = 10) -> List[Dict]:
        """Get recent history."""
        return self._history[-limit:]


# Global agent memory instance
_agent_memory = AgentMemory()


def agent_set_memory(key: str, value: str) -> str:
    """Store a value in agent memory.
    Args:
        key: memory key.
        value: value to store (as string).
    """
    _agent_memory.set(key, value)
    return f"Stored '{key}' in agent memory"


def agent_get_memory(key: str) -> str:
    """Retrieve a value from agent memory.
    Args:
        key: memory key.
    """
    value = _agent_memory.get(key)
    if value is None:
        return f"Key '{key}' not found in memory"
    return str(value)


def agent_list_memory() -> str:
    """List all keys in agent memory."""
    keys = _agent_memory.keys()
    if not keys:
        return "Agent memory is empty"
    return f"Memory keys: {', '.join(keys)}"


def agent_clear_memory() -> str:
    """Clear all agent memory."""
    _agent_memory.clear()
    return "Agent memory cleared"


def agent_memory_history(limit: int = 10) -> str:
    """Get agent memory history.
    Args:
        limit: number of history entries.
    """
    history = _agent_memory.history(limit)
    return json.dumps(history, indent=2)


def agent_think(thought: str) -> str:
    """Record a thought in agent memory for reasoning trace.
    Args:
        thought: the thought to record.
    """
    key = f"thought_{int(time.time())}"
    _agent_memory.set(key, thought)
    return f"Thought recorded: {thought[:50]}..."


def agent_plan(steps: str) -> str:
    """Store a plan in agent memory.
    Args:
        steps: plan steps (newline separated).
    """
    _agent_memory.set('current_plan', steps)
    return f"Plan stored with {len(steps.splitlines())} steps"


def agent_get_plan() -> str:
    """Retrieve current plan from memory."""
    plan = _agent_memory.get('current_plan')
    if plan is None:
        return "No current plan"
    return plan


def agent_goal(goal: str) -> str:
    """Set the current agent goal.
    Args:
        goal: the goal description.
    """
    _agent_memory.set('current_goal', goal)
    return f"Goal set: {goal[:100]}..."


def agent_get_goal() -> str:
    """Retrieve current goal from memory."""
    goal = _agent_memory.get('current_goal')
    if goal is None:
        return "No current goal"
    return goal


def agent_context(data: str) -> str:
    """Add context to agent memory.
    Args:
        data: context information.
    """
    contexts = _agent_memory.get('contexts', [])
    if not isinstance(contexts, list):
        contexts = []
    contexts.append(data)
    _agent_memory.set('contexts', contexts)
    return f"Context added ({len(contexts)} total)"


def agent_get_context() -> str:
    """Retrieve all context from memory."""
    contexts = _agent_memory.get('contexts', [])
    if not contexts:
        return "No context stored"
    return "\n---\n".join(str(c) for c in contexts)


def agent_clear_context() -> str:
    """Clear all context from memory."""
    _agent_memory.delete('contexts')
    return "Context cleared"


def agent_state(state: str) -> str:
    """Set agent state.
    Args:
        state: current state (e.g., 'working', 'waiting', 'error').
    """
    _agent_memory.set('state', state)
    return f"State set to: {state}"


def agent_get_state() -> str:
    """Get current agent state."""
    return _agent_memory.get('state', 'idle')


def agent_metadata(key: str, value: str) -> str:
    """Store metadata about the agent session.
    Args:
        key: metadata key.
        value: metadata value.
    """
    metadata = _agent_memory.get('metadata', {})
    if not isinstance(metadata, dict):
        metadata = {}
    metadata[key] = value
    _agent_memory.set('metadata', metadata)
    return f"Metadata '{key}' stored"


def agent_get_metadata() -> str:
    """Get all agent metadata."""
    metadata = _agent_memory.get('metadata', {})
    if not metadata:
        return "No metadata"
    return json.dumps(metadata, indent=2)


def agent_task_start(task: str) -> str:
    """Mark a task as started.
    Args:
        task: task description.
    """
    _agent_memory.set('current_task', task)
    _agent_memory.set('task_started_at', datetime.now().isoformat())
    return f"Task started: {task[:50]}..."


def agent_task_complete(result: str) -> str:
    """Mark current task as complete.
    Args:
        result: task result summary.
    """
    _agent_memory.set('last_task_result', result)
    _agent_memory.set('task_completed_at', datetime.now().isoformat())
    return f"Task completed: {result[:50]}..."


def agent_error(error: str) -> str:
    """Record an error in agent memory.
    Args:
        error: error description.
    """
    errors = _agent_memory.get('errors', [])
    if not isinstance(errors, list):
        errors = []
    errors.append({
        'error': error,
        'timestamp': datetime.now().isoformat()
    })
    _agent_memory.set('errors', errors)
    return f"Error recorded: {error[:50]}..."


def agent_get_errors() -> str:
    """Get all recorded errors."""
    errors = _agent_memory.get('errors', [])
    if not errors:
        return "No errors recorded"
    return json.dumps(errors, indent=2)


def agent_stats() -> str:
    """Get agent statistics."""
    return json.dumps({
        'memory_keys': len(_agent_memory.keys()),
        'history_entries': len(_agent_memory.history(100)),
        'timestamp': datetime.now().isoformat()
    }, indent=2)


def agent_reset() -> str:
    """Full agent reset - clear all memory."""
    _agent_memory.clear()
    return "Agent fully reset"
