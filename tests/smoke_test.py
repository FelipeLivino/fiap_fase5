from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


BASE_URL = os.getenv("SMOKE_BASE_URL", "http://cardioia-app:5000").rstrip("/")


def request(
    path: str,
    *,
    method: str = "GET",
    payload: object | None = None,
    content_type: str = "application/json",
):
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = content_type
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode("utf-8")
            return response.status, body
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: esperado={expected!r}, obtido={actual!r}")


def main() -> int:
    status, body = request("/health")
    assert_equal(status, 200, "health status")
    assert_equal(json.loads(body)["status"], "ok", "health body")

    status, body = request("/")
    assert_equal(status, 200, "index status")
    if "CardioIA" not in body:
        raise AssertionError("index não contém o nome CardioIA")

    status, _ = request("/api/chat", method="POST", payload={"message": "   "})
    assert_equal(status, 400, "blank message")

    status, _ = request(
        "/api/chat",
        method="POST",
        payload={"message": "Olá"},
        content_type="text/plain",
    )
    assert_equal(status, 415, "unsupported content type")

    status, body = request("/api/chat", method="POST", payload={"message": "Olá"})
    assert_equal(status, 200, "chat status")
    payload = json.loads(body)
    conversation_id = payload.get("conversation_id")
    if not conversation_id or not payload.get("messages"):
        raise AssertionError("resposta de chat incompleta")

    status, body = request(
        "/api/chat",
        method="POST",
        payload={"message": "Teste de contexto", "conversation_id": conversation_id},
    )
    assert_equal(status, 200, "chat continuation")
    assert_equal(json.loads(body)["conversation_id"], conversation_id, "conversation id")

    status, body = request(
        "/api/chat",
        method="POST",
        payload={"message": "Estou com dor forte no peito"},
    )
    assert_equal(status, 200, "urgent mock status")
    if "SAMU 192" not in json.loads(body)["messages"][0]["text"]:
        raise AssertionError("fluxo de urgência não contém orientação fixa")

    status, _ = request(
        f"/api/conversations/{conversation_id}",
        method="DELETE",
    )
    assert_equal(status, 204, "conversation delete")

    status, _ = request(
        "/api/chat",
        method="POST",
        payload={"message": "Continuar", "conversation_id": conversation_id},
    )
    assert_equal(status, 410, "deleted conversation")

    print("smoke_tests=passed checks=9")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"smoke_tests=failed error={type(exc).__name__}", file=sys.stderr)
        raise
