from __future__ import annotations

import math
import re
from collections import Counter, defaultdict


class NaiveBayesTextClassifier:
    """Classificador didático treinado somente com frases sintéticas."""

    TRAINING = {
        "atencao_simulada": [
            "esqueci uma dose no cenário de teste",
            "não consegui seguir a rotina fictícia",
            "senti palpitação forte no exemplo",
            "a medição simulada ficou muito diferente",
        ],
        "rotina_simulada": [
            "tomei a dose fictícia conforme combinado",
            "mensagem de teste sem alteração",
            "rotina simulada concluída normalmente",
            "registro acadêmico está estável",
        ],
    }

    def __init__(self) -> None:
        self._documents: dict[str, int] = {}
        self._counts: dict[str, Counter[str]] = {}
        vocabulary: set[str] = set()
        for label, examples in self.TRAINING.items():
            tokens = Counter(token for text in examples for token in self._tokens(text))
            self._counts[label] = tokens
            self._documents[label] = len(examples)
            vocabulary.update(tokens)
        self._vocabulary = vocabulary

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-záàâãéêíóôõúç]+", text.casefold())

    def classify(self, text: str) -> tuple[str, float]:
        tokens = self._tokens(text)
        total_documents = sum(self._documents.values())
        scores: dict[str, float] = {}
        for label, document_count in self._documents.items():
            score = math.log(document_count / total_documents)
            word_counts = self._counts[label]
            denominator = sum(word_counts.values()) + len(self._vocabulary)
            for token in tokens:
                score += math.log((word_counts[token] + 1) / denominator)
            scores[label] = score
        best = max(scores, key=scores.get)
        exp_scores = {label: math.exp(score - max(scores.values())) for label, score in scores.items()}
        confidence = exp_scores[best] / sum(exp_scores.values())
        return best, round(confidence, 4)


class StatisticalAnomalyDetector:
    """Detecção ilustrativa por z-score sobre uma base sintética fixa."""

    BASELINE = {
        "pressao_sistolica": [108, 112, 115, 118, 120, 122, 125, 117],
        "pressao_diastolica": [68, 70, 72, 75, 78, 80, 76, 74],
        "frequencia_cardiaca": [62, 66, 70, 72, 75, 78, 80, 68],
    }

    def __init__(self, threshold: float = 2.5) -> None:
        self._threshold = threshold

    def detect(self, reading: dict[str, object]) -> list[str]:
        reasons: list[str] = []
        for field, baseline in self.BASELINE.items():
            mean = sum(baseline) / len(baseline)
            variance = sum((value - mean) ** 2 for value in baseline) / len(baseline)
            standard_deviation = math.sqrt(variance)
            value = float(reading[field])
            z_score = abs(value - mean) / standard_deviation
            if z_score >= self._threshold:
                reasons.append(f"anomalia_estatistica_{field}")
        if reading.get("adesao_tratamento") == "nao":
            reasons.append("adesao_ficticia_nao_confirmada")
        return reasons
