"""Session Memory Buffer for SET Financial Assistant.

Maintains multi-turn context, rolling window memory, and query reformulation
for follow-up questions (e.g. 'what about last month', 'which was highest').
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ConversationTurn:
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float = field(default_factory=time.time)


class SessionMemoryBuffer:
    """Sliding-window conversational memory buffer."""

    def __init__(self, max_turns: int = 8):
        self.max_turns = max_turns
        self._history: List[ConversationTurn] = []

    def load_from_history(self, history: List[Dict[str, Any]]):
        """Loads and normalizes raw history list from frontend."""
        self._history = []
        if not history:
            return
        for turn in history:
            role_raw = (turn.get("role") or turn.get("sender") or "").lower()
            text = (turn.get("text") or turn.get("content") or "").strip()
            if not text:
                continue
            role = "assistant" if role_raw in {"assistant", "bot", "ai", "set"} else "user"
            self._history.append(ConversationTurn(role=role, content=text))
        self._trim()

    def add_user_message(self, text: str):
        self._history.append(ConversationTurn(role="user", content=text.strip()))
        self._trim()

    def add_bot_message(self, text: str):
        self._history.append(ConversationTurn(role="assistant", content=text.strip()))
        self._trim()

    def get_context_tuples(self) -> List[Dict[str, str]]:
        return [{"role": t.role, "text": t.content} for t in self._history]

    def _trim(self):
        max_items = self.max_turns * 2
        if len(self._history) > max_items:
            self._history = self._history[-max_items:]

    def rewrite_query_with_context(self, current_query: str) -> str:
        """Reformulates contextual follow-ups into standalone search queries.
        
        Example:
        Turn 1: "How much did I spend on Swiggy in August?"
        Turn 2: "What about Zomato?"
        -> Rewritten: "How much did I spend on Zomato in August?"
        """
        q = current_query.strip()
        if not self._history or not q:
            return q

        q_lower = q.lower()
        pronoun_triggers = [
            "it", "those", "them", "that", "that one", "these",
            "same", "there", "what about", "how about", "and for",
            "show more", "list them", "which was", "which one"
        ]

        is_followup = any(p in q_lower for p in pronoun_triggers) or len(q.split()) <= 4
        if not is_followup:
            return q

        # Find the last user query
        user_turns = [t.content for t in self._history if t.role == "user"]
        if not user_turns:
            return q

        last_user_query = user_turns[-1]
        
        # If user asks "what about Zomato"
        if q_lower.startswith(("what about", "how about", "and for", "and")):
            target = q
            for prefix in ["what about", "how about", "and for", "and"]:
                if q_lower.startswith(prefix):
                    target = q[len(prefix):].strip(" ?.,")
                    break
            if target:
                return f"{last_user_query} (Follow-up target: {target})"

        # If user asks "which was the highest/lowest/largest"
        if any(w in q_lower for w in ["highest", "largest", "maximum", "lowest", "smallest", "cheapest", "costliest"]):
            return f"{last_user_query} (Find extrema: {q})"

        return f"{last_user_query} | Follow-up: {q}"
