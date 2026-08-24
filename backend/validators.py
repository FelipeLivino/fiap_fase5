from __future__ import annotations


class MessageValidationError(Exception):
    pass


def validate_message(value: object, max_chars: int) -> str:
    if not isinstance(value, str):
        raise MessageValidationError("O campo 'message' deve ser um texto.")
    message = value.strip()
    if not message:
        raise MessageValidationError("Digite uma mensagem antes de enviar.")
    if len(message) > max_chars:
        raise MessageValidationError(
            f"A mensagem deve ter no máximo {max_chars} caracteres."
        )
    return message
