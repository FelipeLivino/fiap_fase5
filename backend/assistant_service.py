from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.conversation_service import Conversation
from config import Settings


@dataclass(frozen=True)
class AssistantReply:
    messages: tuple[str, ...]
    intent: str


class AssistantUnavailableError(Exception):
    """Falha controlada do provedor, sem incluir conteúdo ou segredo."""


logger = logging.getLogger(__name__)


class MockAssistantService:
    """Resposta determinística temporária para validar a fundação da Fase 1."""

    _urgent_terms = (
        "dor forte no peito",
        "falta de ar intensa",
        "desmaiei",
        "suor frio",
    )

    def respond(self, message: str, conversation: Conversation) -> AssistantReply:
        normalized = message.casefold()
        context = conversation.context
        context["turn_count"] = int(context.get("turn_count", 0)) + 1

        if any(term in normalized for term in self._urgent_terms):
            return AssistantReply(
                messages=((
                    "Isso pode ser uma urgência. No Brasil, ligue agora para o "
                    "SAMU 192 ou procure imediatamente um serviço de emergência. "
                    "Não espere uma resposta deste assistente."
                ),),
                intent="sinal_urgencia_mock",
            )

        if any(term in normalized for term in ("olá", "ola", "oi", "bom dia")):
            return AssistantReply(
                messages=((
                    "Olá! Sou o CardioIA em modo de fundação. Nesta fase, as respostas "
                    "são simuladas para validar a interface e o backend em Docker."
                ),),
                intent="saudacao_mock",
            )

        return AssistantReply(
            messages=((
                "Mensagem recebida pelo backend conteinerizado. A interpretação pelo "
                "IBM Watson Assistant será conectada na Fase 3."
            ),),
            intent="fallback_mock",
        )

    def close(self, _conversation: Conversation | None) -> None:
        return None


class WatsonAssistantService:
    """Adaptador para runtime Watson v2 stateful ou workspace v1."""

    def __init__(self, settings: Settings, *, client: Any | None = None) -> None:
        self._settings = settings
        self._profile = settings.watson_api_profile
        self._assistant_id = settings.watson_assistant_id
        self._environment_id = settings.watson_environment_id
        self._workspace_id = settings.watson_workspace_id
        self._client = client or self._build_client(settings)

    @staticmethod
    def _build_client(settings: Settings):
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibm_watson import AssistantV1, AssistantV2

        api_key = Path(settings.watson_api_key_file).read_text(encoding="utf-8").strip()
        authenticator = IAMAuthenticator(api_key)
        if settings.watson_api_profile == "v2":
            client = AssistantV2(
                version=settings.watson_api_version,
                authenticator=authenticator,
            )
        else:
            client = AssistantV1(
                version=settings.watson_api_version,
                authenticator=authenticator,
            )
        client.set_service_url(settings.watson_service_url)
        client.set_http_config({"timeout": settings.watson_timeout_seconds})
        return client

    def respond(self, message: str, conversation: Conversation) -> AssistantReply:
        try:
            if self._profile == "v2":
                result = self._respond_v2(message, conversation)
            else:
                result = self._respond_v1(message, conversation)
        except Exception as exc:
            logger.warning("watson_request_failed error_type=%s", type(exc).__name__)
            raise AssistantUnavailableError from exc

        messages = self._extract_messages(result)
        if not messages:
            raise AssistantUnavailableError("watson_empty_response")
        return AssistantReply(messages=messages, intent=self._extract_intent(result))

    def _respond_v2(self, message: str, conversation: Conversation) -> dict[str, Any]:
        if not conversation.provider_session_id:
            session = self._client.create_session(
                assistant_id=self._assistant_id,
                environment_id=self._environment_id,
            ).get_result()
            conversation.provider_session_id = session["session_id"]
        return self._client.message(
            assistant_id=self._assistant_id,
            environment_id=self._environment_id,
            session_id=conversation.provider_session_id,
            input={"message_type": "text", "text": message},
            user_id=conversation.conversation_id,
        ).get_result()

    def _respond_v1(self, message: str, conversation: Conversation) -> dict[str, Any]:
        result = self._client.message(
            workspace_id=self._workspace_id,
            input={"text": message},
            context=conversation.context,
        ).get_result()
        context = result.get("context")
        if isinstance(context, dict):
            conversation.context = context
        return result

    def close(self, conversation: Conversation | None) -> None:
        if (
            self._profile != "v2"
            or conversation is None
            or not conversation.provider_session_id
        ):
            return
        try:
            self._client.delete_session(
                assistant_id=self._assistant_id,
                environment_id=self._environment_id,
                session_id=conversation.provider_session_id,
            ).get_result()
        except Exception as exc:
            logger.warning("watson_session_delete_failed error_type=%s", type(exc).__name__)

    @staticmethod
    def _extract_messages(result: dict[str, Any]) -> tuple[str, ...]:
        output = result.get("output", {})
        messages: list[str] = []
        generic = output.get("generic", []) if isinstance(output, dict) else []
        for item in generic:
            if isinstance(item, dict) and item.get("response_type") == "text":
                value = item.get("text")
                if isinstance(value, str) and value.strip():
                    messages.append(value.strip())
        if not messages and isinstance(output, dict):
            legacy_text = output.get("text", [])
            if isinstance(legacy_text, str):
                legacy_text = [legacy_text]
            for value in legacy_text if isinstance(legacy_text, list) else []:
                if isinstance(value, str) and value.strip():
                    messages.append(value.strip())
        return tuple(messages)

    @staticmethod
    def _extract_intent(result: dict[str, Any]) -> str:
        output = result.get("output", {})
        intents = output.get("intents", []) if isinstance(output, dict) else []
        if not intents:
            intents = result.get("intents", [])
        if isinstance(intents, list) and intents and isinstance(intents[0], dict):
            value = intents[0].get("intent")
            if isinstance(value, str) and value:
                return value
        return "sem_intent"
