from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Sintoma(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=1, max_length=80)
    duracao: str | None = Field(default=None, max_length=80)
    intensidade: Literal["leve", "moderada", "forte"] | None = None


class Medida(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Literal[
        "frequencia_cardiaca",
        "pressao_sistolica",
        "pressao_diastolica",
    ]
    valor: float | None = None
    unidade: Literal["bpm", "mmHg"] | None = None


class ExtracaoClinica(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "needs_review"]
    sintomas: list[Sintoma]
    medidas: list[Medida]
    medicamentos_mencionados: list[str]
    campos_ausentes: list[str]
    inconsistencias: list[str]
    trechos_fonte: list[str]
    observacao: str = Field(
        default="Dados extraídos de cenário fictício; não constituem avaliação médica."
    )
