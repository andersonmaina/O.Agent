import re
from typing import List, Dict, Tuple
from core.config import settings

class SmartContextManager:
    """
    Implements recursive token optimization (RTK-like) and sliding window.
    Features:
    - Recursive summarization of old history.
    - Semantic deduplication (basic).
    - Hard truncation as a fallback.
    """

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // settings.TOKEN_ESTIMATE_PER_CHAR

    def optimize(self, messages: List[Dict[str, str]], max_tokens: int = None) -> List[Dict[str, str]]:
        max_tokens = max_tokens or settings.MAX_CONTEXT_TOKENS
        
        # 1. Deduplicate consecutive identical messages (user/user or assistant/assistant)
        messages = self.deduplicate(messages)

        current_tokens = sum(self.estimate_tokens(m['content']) for m in messages)

        if current_tokens <= max_tokens * settings.SUMMARY_TRIGGER_RATIO:
            return messages

        # 2. Recursive Compression (RTK Logic)
        # Summarize older half if we are over trigger ratio
        summary_ratio = 0.5
        split_index = int(len(messages) * summary_ratio)
        
        old_history = messages[:split_index]
        recent_history = messages[split_index:]
        
        # In a real RTK system, we'd use another LLM call here to summarize old_history.
        # But for now, we'll provide a 'compressed' representation.
        summary_content = self.generate_session_summary(old_history)
        
        optimized = [
            {'role': 'system', 'content': f"CONSOLIDATED HISTORY SUMMARY: {summary_content}"}
        ] + recent_history

        # 3. Final safety truncation
        return self.truncate_to_limit(optimized, max_tokens)

    def deduplicate(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if not messages: return []
        new_messages = [messages[0]]
        for m in messages[1:]:
            # If same role and same content (or very similar), skip
            if m['role'] == new_messages[-1]['role'] and m['content'] == new_messages[-1]['content']:
                continue
            new_messages.append(m)
        return new_messages

    def generate_session_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Skeleton for recursive summarization. 
        In production, this should call an LLM to 'compress' the messages.
        """
        summary_parts = []
        for m in messages:
            content_snippet = m['content'][:100].replace('\n', ' ')
            summary_parts.append(f"[{m['role']}]: {content_snippet}")
        
        return " | ".join(summary_parts)

    def truncate_to_limit(self, messages: List[Dict[str, str]], limit: int) -> List[Dict[str, str]]:
        result = []
        total = 0
        # Always keep system messages
        system_msgs = [m for m in messages if m['role'] == 'system']
        for m in system_msgs:
            total += self.estimate_tokens(m['content'])
            result.append(m)
        
        other_msgs = [m for m in messages if m['role'] != 'system']
        # Add from end to beginning
        accumulated = []
        for m in reversed(other_msgs):
            tokens = self.estimate_tokens(m['content'])
            if total + tokens > limit:
                break
            accumulated.insert(0, m)
            total += tokens
            
        return result + accumulated
