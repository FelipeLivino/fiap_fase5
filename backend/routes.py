from __future__ import annotations

import logging
import uuid

from flask import Blueprint, current_app, jsonify, render_template, request

from backend.assistant_service import AssistantUnavailableError
from backend.conversation_service import ConversationExpiredError
from backend.validators import MessageValidationError, validate_message


web = Blueprint("web", __name__)
logger = logging.getLogger(__name__)


def _error(code: str, message: str, status: int, request_id: str):
    return jsonify(error={"code": code, "message": message, "request_id": request_id}), status


@web.get("/")
def index():
    return render_template(
        "index.html", assistant_mode=current_app.config["ASSISTANT_MODE"]
    )


@web.get("/health")
def health():
    return jsonify(status="ok", service="cardioia-api")


@web.post("/api/chat")
def chat():
    request_id = uuid.uuid4().hex[:12]
    if not request.is_json:
        return _error(
            "UNSUPPORTED_MEDIA_TYPE",
            "Envie a requisição como application/json.",
            415,
            request_id,
        )

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("INVALID_JSON", "JSON inválido.", 400, request_id)

    try:
        message = validate_message(
            payload.get("message"), current_app.config["MAX_MESSAGE_CHARS"]
        )
    except MessageValidationError as exc:
        return _error("INVALID_MESSAGE", str(exc), 400, request_id)

    conversation_store = current_app.extensions["conversation_store"]
    try:
        conversation = conversation_store.get_or_create(payload.get("conversation_id"))
    except ConversationExpiredError:
        return _error(
            "CONVERSATION_EXPIRED",
            "A conversa expirou. Inicie uma nova conversa.",
            410,
            request_id,
        )

    assistant_service = current_app.extensions["assistant_service"]
    try:
        with conversation.lock:
            reply = assistant_service.respond(message, conversation)
    except AssistantUnavailableError:
        logger.warning("chat_provider_unavailable request_id=%s status=503", request_id)
        return _error(
            "ASSISTANT_UNAVAILABLE",
            "O assistente está temporariamente indisponível. Tente novamente. "
            "Em uma urgência no Brasil, ligue para o SAMU 192 ou procure um "
            "serviço de emergência.",
            503,
            request_id,
        )

    logger.info(
        "chat_completed request_id=%s intent=%s status=200",
        request_id,
        reply.intent,
    )
    return jsonify(
        messages=[{"type": "text", "text": text} for text in reply.messages],
        conversation_id=conversation.conversation_id,
        metadata={"intent": reply.intent, "mode": current_app.config["ASSISTANT_MODE"]},
        request_id=request_id,
    )


@web.delete("/api/conversations/<conversation_id>")
def delete_conversation(conversation_id: str):
    conversation = current_app.extensions["conversation_store"].delete(conversation_id)
    current_app.extensions["assistant_service"].close(conversation)
    return "", 204
