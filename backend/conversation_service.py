from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field


class ConversationExpiredError(Exception):
    pass


@dataclass
class Conversation:
    conversation_id: str
    context: dict[str, object]
    last_seen: float
    provider_session_id: str | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)


class ConversationStore:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl_seconds = ttl_seconds
        self._items: dict[str, Conversation] = {}
        self._lock = threading.Lock()

    def get_or_create(self, conversation_id: str | None) -> Conversation:
        now = time.monotonic()
        with self._lock:
            self._remove_expired(now)
            if conversation_id is None:
                new_id = str(uuid.uuid4())
                conversation = Conversation(new_id, {}, now)
                self._items[new_id] = conversation
                return conversation

            try:
                canonical_id = str(uuid.UUID(conversation_id))
            except (ValueError, AttributeError, TypeError) as exc:
                raise ConversationExpiredError from exc

            conversation = self._items.get(canonical_id)
            if conversation is None:
                raise ConversationExpiredError
            conversation.last_seen = now
            return conversation

    def delete(self, conversation_id: str) -> Conversation | None:
        with self._lock:
            return self._items.pop(conversation_id, None)

    def _remove_expired(self, now: float) -> None:
        expired = [
            conversation_id
            for conversation_id, conversation in self._items.items()
            if now - conversation.last_seen > self._ttl_seconds
        ]
        for conversation_id in expired:
            del self._items[conversation_id]
