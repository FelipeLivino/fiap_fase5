from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from backend.assistant_service import (
    AssistantUnavailableError,
    WatsonAssistantService,
)
from backend.conversation_service import Conversation


class FakeResponse:
    def __init__(self, value):
        self._value = value

    def get_result(self):
        return self._value


class FakeV2Client:
    def __init__(self, *, empty: bool = False):
        self.empty = empty
        self.deleted: list[str] = []

    def create_session(self, **_kwargs):
        return FakeResponse({"session_id": "provider-secret-id"})

    def message(self, **_kwargs):
        generic = [] if self.empty else [
            {"response_type": "text", "text": "Primeira resposta"},
            {"response_type": "text", "text": "Segunda resposta"},
        ]
        return FakeResponse(
            {"output": {"generic": generic, "intents": [{"intent": "saudacao"}]}}
        )

    def delete_session(self, **kwargs):
        self.deleted.append(kwargs["session_id"])
        return FakeResponse({})


class FakeV1Client:
    def message(self, **_kwargs):
        return FakeResponse(
            {
                "output": {"text": ["Resposta clássica"]},
                "intents": [{"intent": "ajuda"}],
                "context": {"turno": 2},
            }
        )


def settings(profile: str):
    return SimpleNamespace(
        watson_api_profile=profile,
        watson_environment_id="environment-id" if profile == "v2" else "",
        watson_assistant_id="assistant-id" if profile == "v2" else "",
        watson_workspace_id="workspace-id" if profile == "v1" else "",
    )


def main() -> int:
    conversation = Conversation("public-id", {}, 0.0)
    v2_client = FakeV2Client()
    service = WatsonAssistantService(settings("v2"), client=v2_client)
    reply = service.respond("Olá", conversation)
    assert reply.messages == ("Primeira resposta", "Segunda resposta")
    assert reply.intent == "saudacao"
    assert conversation.provider_session_id == "provider-secret-id"
    service.close(conversation)
    assert v2_client.deleted == ["provider-secret-id"]

    v1_conversation = Conversation("public-id-v1", {}, 0.0)
    v1_service = WatsonAssistantService(settings("v1"), client=FakeV1Client())
    reply = v1_service.respond("Ajuda", v1_conversation)
    assert reply.messages == ("Resposta clássica",)
    assert reply.intent == "ajuda"
    assert v1_conversation.context == {"turno": 2}

    empty_service = WatsonAssistantService(
        settings("v2"), client=FakeV2Client(empty=True)
    )
    try:
        empty_service.respond("Teste", Conversation("empty", {}, 0.0))
    except AssistantUnavailableError:
        pass
    else:
        raise AssertionError("resposta Watson vazia deveria gerar erro controlado")

    export = json.loads(Path("watson/assistant-export.json").read_text(encoding="utf-8"))
    intents = {item["intent"] for item in export["intents"]}
    required = {
        "saudacao",
        "ajuda",
        "relatar_sintoma",
        "confirmar",
        "negar",
        "encerrar",
        "sinal_urgencia",
    }
    assert required <= intents
    assert export["dialog_nodes"][-1]["conditions"] == "anything_else"
    assert "SAMU 192" in json.dumps(export, ensure_ascii=False)

    print("unit_tests=passed checks=13")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
