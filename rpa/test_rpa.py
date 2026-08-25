from __future__ import annotations

import os
from urllib.parse import quote_plus

import psycopg
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


def secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Variável de ambiente obrigatória ausente: {name}")
    return value


def expect_failure(callback, label: str) -> None:
    try:
        callback()
    except Exception:
        return
    raise AssertionError(f"{label} deveria ser rejeitado")


def main() -> int:
    pg_password = secret("RPA_POSTGRES_PASSWORD")
    pg_dsn = (
        "host=rpa-postgres dbname=cardioia user=cardioia_rpa "
        f"password={pg_password} connect_timeout=5"
    )
    with psycopg.connect(pg_dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM leituras_simuladas WHERE processado_em IS NULL")
            assert cursor.fetchone()[0] == 0

    expect_failure(
        lambda: psycopg.connect(
            "host=rpa-postgres dbname=cardioia user=cardioia_rpa password=incorreta connect_timeout=3"
        ),
        "senha PostgreSQL incorreta",
    )
    expect_failure(
        lambda: _attempt_postgres_admin(pg_dsn),
        "privilégio administrativo PostgreSQL",
    )

    mongo_password = quote_plus(secret("RPA_MONGO_PASSWORD"))
    client = MongoClient(
        f"mongodb://cardioia_rpa:{mongo_password}@rpa-mongo:27017/cardioia?authSource=cardioia",
        serverSelectionTimeoutMS=3000,
    )
    database = client.cardioia
    assert database.execucoes.count_documents({"status": "concluido"}) >= 2
    events = list(database.eventos.find({}))
    assert len(events) >= 5
    assert len(events) == len({event["fonte_chave"] for event in events})
    assert any(event["resultado"] == "alerta_simulado" for event in events)
    assert any(event["fonte_tipo"] == "mensagem" for event in events)
    assert all(event["acao_externa_executada"] is False for event in events)

    expect_failure(
        lambda: MongoClient(
            "mongodb://rpa-mongo:27017", serverSelectionTimeoutMS=2000
        ).cardioia.eventos.find_one(),
        "acesso MongoDB anônimo",
    )
    expect_failure(
        lambda: MongoClient(
            "mongodb://cardioia_rpa:incorreta@rpa-mongo:27017/cardioia?authSource=cardioia",
            serverSelectionTimeoutMS=2000,
        ).cardioia.eventos.find_one(),
        "senha MongoDB incorreta",
    )
    expect_failure(
        lambda: client.admin.command("serverStatus"),
        "privilégio administrativo MongoDB",
    )

    print("rpa_tests=passed checks=13")
    return 0


def _attempt_postgres_admin(dsn: str) -> None:
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE tentativa_admin_bloqueada (id integer)")


if __name__ == "__main__":
    raise SystemExit(main())
