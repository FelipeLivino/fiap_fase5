from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


BASE_URL = os.getenv("SMOKE_BASE_URL", "http://cardioia-app:5000").rstrip("/")

CASES = (
    ("W-01", "Boa tarde, quero começar", "saudacao", None),
    ("W-02", "Que tipo de simulação você aceita?", "ajuda", None),
    (
        "W-03",
        "No exemplo meu coração ficou acelerado por dez minutos",
        "relatar_sintoma",
        None,
    ),
    ("W-04", "Sim, o registro está certo", "confirmar", None),
    ("W-05", "Quero alterar o que escrevi", "negar", None),
    ("W-06", "Até mais, pode finalizar", "encerrar", None),
    (
        "W-07",
        "Dor muito forte no peito e suor frio",
        "sinal_urgencia",
        "SAMU 192",
    ),
    ("W-08", "Fale sobre astronomia", "sem_intent", None),
    ("W-09", "Qual medicamento devo tomar?", "sem_intent", None),
)


def chat(message: str) -> dict:
    body = json.dumps({"message": message}).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise AssertionError(f"status inesperado: {response.status}")
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise AssertionError(f"status inesperado: {error.code}") from error


def main() -> int:
    approved = 0
    failures: list[str] = []
    for case_id, message, expected_intent, required_text in CASES:
        result = chat(message)
        actual_intent = result.get("metadata", {}).get("intent")
        mode = result.get("metadata", {}).get("mode")
        texts = [item.get("text", "") for item in result.get("messages", [])]
        reason = None
        if mode != "watson":
            reason = f"modo={mode!r}"
        elif actual_intent != expected_intent:
            reason = f"esperado={expected_intent!r} obtido={actual_intent!r}"
        elif required_text and not any(required_text in text for text in texts):
            reason = "texto_de_seguranca_ausente"
        if reason:
            failures.append(f"{case_id}: {reason}")
            print(f"{case_id}=failed intent={actual_intent}")
        else:
            approved += 1
            print(f"{case_id}=passed intent={actual_intent}")
    if failures:
        raise AssertionError("; ".join(failures))
    print(f"watson_live_tests=passed checks={approved}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"watson_live_tests=failed error={type(exc).__name__}", file=sys.stderr)
        raise
