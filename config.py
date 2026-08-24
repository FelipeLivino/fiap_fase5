from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(name: str, default: int, *, minimum: int = 1) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} deve ser um número inteiro.") from exc
    if value < minimum:
        raise RuntimeError(f"{name} deve ser maior ou igual a {minimum}.")
    return value


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_debug: bool
    app_host: str
    app_port: int
    log_level: str
    assistant_mode: str
    max_message_chars: int
    conversation_ttl_seconds: int
    watson_api_key_file: str
    watson_api_profile: str
    watson_service_url: str
    watson_assistant_id: str
    watson_environment_id: str
    watson_workspace_id: str
    watson_api_version: str
    watson_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        assistant_mode = os.getenv("ASSISTANT_MODE", "mock").strip().lower()
        if assistant_mode not in {"mock", "watson"}:
            raise RuntimeError("ASSISTANT_MODE deve ser 'mock' ou 'watson'.")

        settings = cls(
            app_env=os.getenv("APP_ENV", "development"),
            app_debug=_as_bool(os.getenv("APP_DEBUG")),
            app_host=os.getenv("APP_HOST", "0.0.0.0"),
            app_port=_as_int("APP_PORT", 5000, minimum=1),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            assistant_mode=assistant_mode,
            max_message_chars=_as_int("MAX_MESSAGE_CHARS", 1000, minimum=1),
            conversation_ttl_seconds=_as_int(
                "CONVERSATION_TTL_SECONDS", 900, minimum=30
            ),
            watson_api_key_file=os.getenv(
                "WATSON_API_KEY_FILE", "/run/secrets/watson_api_key"
            ),
            watson_api_profile=os.getenv("WATSON_API_PROFILE", "v2").strip().lower(),
            watson_service_url=os.getenv("WATSON_SERVICE_URL", "").strip(),
            watson_assistant_id=os.getenv("WATSON_ASSISTANT_ID", "").strip(),
            watson_environment_id=os.getenv("WATSON_ENVIRONMENT_ID", "").strip(),
            watson_workspace_id=os.getenv("WATSON_WORKSPACE_ID", "").strip(),
            watson_api_version=os.getenv("WATSON_API_VERSION", "").strip(),
            watson_timeout_seconds=_as_int("WATSON_TIMEOUT_SECONDS", 10, minimum=1),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if not 1 <= self.app_port <= 65535:
            raise RuntimeError("APP_PORT deve estar entre 1 e 65535.")

        if self.assistant_mode != "watson":
            return

        if self.watson_api_profile not in {"v1", "v2"}:
            raise RuntimeError("WATSON_API_PROFILE deve ser 'v1' ou 'v2'.")

        required_values = {
            "WATSON_SERVICE_URL": self.watson_service_url,
            "WATSON_API_VERSION": self.watson_api_version,
        }
        missing = [name for name, value in required_values.items() if not value]
        if self.watson_api_profile == "v2":
            if not self.watson_assistant_id:
                missing.append("WATSON_ASSISTANT_ID")
            if not self.watson_environment_id:
                missing.append("WATSON_ENVIRONMENT_ID")
        if self.watson_api_profile == "v1" and not self.watson_workspace_id:
            missing.append("WATSON_WORKSPACE_ID")
        if missing:
            raise RuntimeError(
                "Configuração Watson incompleta: " + ", ".join(sorted(missing))
            )

        secret_path = Path(self.watson_api_key_file)
        if not secret_path.is_file():
            raise RuntimeError("Secret file do Watson não foi encontrado.")
        if secret_path.read_text(encoding="utf-8").strip() in {"", "mock-not-used"}:
            raise RuntimeError("Secret file do Watson ainda contém um placeholder.")
