from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from backend.assistant_service import MockAssistantService, WatsonAssistantService
from backend.conversation_service import ConversationStore
from backend.routes import web
from config import Settings


def create_app(settings: Settings) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024,
        MAX_MESSAGE_CHARS=settings.max_message_chars,
        ASSISTANT_MODE=settings.assistant_mode,
    )
    app.json.ensure_ascii = False

    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    app.extensions["conversation_store"] = ConversationStore(
        ttl_seconds=settings.conversation_ttl_seconds
    )
    if settings.assistant_mode == "mock":
        app.extensions["assistant_service"] = MockAssistantService()
    else:
        app.extensions["assistant_service"] = WatsonAssistantService(settings)

    app.register_blueprint(web)

    @app.errorhandler(413)
    def payload_too_large(_error):
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    error={
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "O corpo da requisição excede o limite permitido.",
                    }
                ),
                413,
            )
        return "Conteúdo muito grande.", 413

    return app
