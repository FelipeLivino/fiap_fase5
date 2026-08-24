from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import psycopg
from psycopg.rows import dict_row
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from rpa.ai import NaiveBayesTextClassifier, StatisticalAnomalyDetector


MODEL_VERSION = "naive-bayes-zscore-v1"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def read_secret(env_name: str) -> str:
    path = Path(os.environ[env_name])
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"Secret vazio: {env_name}")
    return value


class RpaWorker:
    def __init__(self) -> None:
        postgres_password = read_secret("RPA_POSTGRES_PASSWORD_FILE")
        mongo_password = read_secret("RPA_MONGO_PASSWORD_FILE")
        self._postgres_dsn = (
            f"host={os.getenv('POSTGRES_HOST', 'rpa-postgres')} "
            f"dbname={os.getenv('POSTGRES_DB', 'cardioia')} "
            f"user={os.getenv('RPA_POSTGRES_USER', 'cardioia_rpa')} "
            f"password={postgres_password} connect_timeout=5"
        )
        mongo_user = quote_plus(os.getenv("RPA_MONGO_USER", "cardioia_rpa"))
        mongo_password_encoded = quote_plus(mongo_password)
        mongo_host = os.getenv("MONGO_HOST", "rpa-mongo")
        self._mongo = MongoClient(
            f"mongodb://{mongo_user}:{mongo_password_encoded}@{mongo_host}:27017/"
            "cardioia?authSource=cardioia",
            serverSelectionTimeoutMS=5000,
        )["cardioia"]
        self._text_classifier = NaiveBayesTextClassifier()
        self._anomaly_detector = StatisticalAnomalyDetector()

    def run_cycle(self) -> None:
        execution_id = str(uuid.uuid4())
        started = utc_now()
        self._mongo.execucoes.insert_one(
            {
                "execucao_id": execution_id,
                "iniciado_em": started,
                "finalizado_em": None,
                "status": "em_andamento",
                "modelo_ou_regra_versao": MODEL_VERSION,
                "leituras_processadas": 0,
                "mensagens_processadas": 0,
                "alertas_simulados": 0,
                "erro_sanitizado": None,
            }
        )
        readings_processed = 0
        messages_processed = 0
        alerts = 0
        try:
            with psycopg.connect(self._postgres_dsn, row_factory=dict_row) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, paciente_simulado_id, coletado_em,
                               pressao_sistolica, pressao_diastolica,
                               frequencia_cardiaca, adesao_tratamento
                          FROM leituras_simuladas
                         WHERE processado_em IS NULL
                         ORDER BY id
                         FOR UPDATE SKIP LOCKED
                        """
                    )
                    readings = cursor.fetchall()
                    for reading in readings:
                        reasons = self._anomaly_detector.detect(reading)
                        outcome = "alerta_simulado" if reasons else "normal_simulado"
                        alerts += int(bool(reasons))
                        self._record_event(
                            source_key=f"leitura:{reading['id']}:{MODEL_VERSION}",
                            source_type="leitura",
                            source_id=str(reading["id"]),
                            simulated_patient=reading["paciente_simulado_id"],
                            outcome=outcome,
                            reasons=reasons,
                            execution_id=execution_id,
                        )
                        cursor.execute(
                            "UPDATE leituras_simuladas SET processado_em = %s WHERE id = %s",
                            (utc_now(), reading["id"]),
                        )
                        readings_processed += 1

            messages = list(
                self._mongo.mensagens.find({"processado_em": None}).sort("criado_em", 1)
            )
            for message in messages:
                label, confidence = self._text_classifier.classify(
                    message["texto_simulado"]
                )
                reasons = [f"classificacao_textual_{label}", f"confianca_{confidence:.4f}"]
                outcome = (
                    "alerta_simulado"
                    if label == "atencao_simulada"
                    else "normal_simulado"
                )
                alerts += int(outcome == "alerta_simulado")
                self._record_event(
                    source_key=f"mensagem:{message['mensagem_id']}:{MODEL_VERSION}",
                    source_type="mensagem",
                    source_id=message["mensagem_id"],
                    simulated_patient=message["paciente_simulado_id"],
                    outcome=outcome,
                    reasons=reasons,
                    execution_id=execution_id,
                )
                self._mongo.mensagens.update_one(
                    {"_id": message["_id"]}, {"$set": {"processado_em": utc_now()}}
                )
                messages_processed += 1

            self._mongo.execucoes.update_one(
                {"execucao_id": execution_id},
                {
                    "$set": {
                        "finalizado_em": utc_now(),
                        "status": "concluido",
                        "leituras_processadas": readings_processed,
                        "mensagens_processadas": messages_processed,
                        "alertas_simulados": alerts,
                    }
                },
            )
            print(
                "rpa_cycle_completed "
                f"execucao_id={execution_id} readings={readings_processed} "
                f"messages={messages_processed} alerts={alerts}"
            )
        except Exception as exc:
            self._mongo.execucoes.update_one(
                {"execucao_id": execution_id},
                {
                    "$set": {
                        "finalizado_em": utc_now(),
                        "status": "erro",
                        "erro_sanitizado": type(exc).__name__,
                    }
                },
            )
            raise

    def _record_event(
        self,
        *,
        source_key: str,
        source_type: str,
        source_id: str,
        simulated_patient: str,
        outcome: str,
        reasons: list[str],
        execution_id: str,
    ) -> None:
        event = {
            "fonte_chave": source_key,
            "fonte_tipo": source_type,
            "fonte_id": source_id,
            "paciente_simulado_id": simulated_patient,
            "execucao_id": execution_id,
            "resultado": outcome,
            "motivos": reasons,
            "modelo_ou_regra_versao": MODEL_VERSION,
            "criado_em": utc_now(),
            "revisao_humana_obrigatoria": True,
            "acao_externa_executada": False,
        }
        try:
            self._mongo.eventos.insert_one(event)
        except DuplicateKeyError:
            return


def main() -> int:
    cycles = int(os.getenv("RPA_MAX_CYCLES", "2"))
    interval = int(os.getenv("RPA_INTERVAL_SECONDS", "2"))
    worker = RpaWorker()
    for cycle in range(cycles):
        worker.run_cycle()
        if cycle + 1 < cycles:
            time.sleep(interval)
    print(f"rpa_worker_completed cycles={cycles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
