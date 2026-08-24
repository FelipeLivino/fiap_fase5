from __future__ import annotations

import json
import os

from backend.assistant_service import AssistantUnavailableError, WatsonAssistantService
from backend.conversation_service import Conversation
from config import Settings


def main() -> int:
    service = WatsonAssistantService(Settings.from_env())
    conversation = Conversation("diagnostic", {}, 0.0)
    try:
        result = service._respond_v2(
            os.getenv("DIAGNOSTIC_MESSAGE", "Olá"),
            conversation,
        )
    except AssistantUnavailableError as error:
        cause = error.__cause__
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_type": type(cause).__name__,
                    "code": getattr(cause, "code", None),
                    "message": getattr(cause, "message", str(cause)),
                },
                ensure_ascii=False,
            )
        )
        return 1
    finally:
        service.close(conversation)

    output = result.get("output", {})
    intents = [
        {"intent": item.get("intent"), "confidence": item.get("confidence")}
        for item in output.get("intents", [])
        if isinstance(item, dict)
    ]
    texts = [
        item.get("text")
        for item in output.get("generic", [])
        if isinstance(item, dict) and item.get("response_type") == "text"
    ]
    print(
        json.dumps(
            {"ok": True, "intents": intents, "response_count": len(texts)},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
