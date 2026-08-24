from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path


V1_SPEC_PATH = Path("watson/assistant-export.json")
EXPORT_PATH = Path(os.getenv("SKILLS_EXPORT_PATH", "/export/skills.json"))
OUTPUT_PATH = Path(os.getenv("SKILLS_IMPORT_PATH", "/export/actions-import.json"))

RESPONSES = {
    "saudacao": (
        "Saudação",
        "Olá! Posso organizar um relato inicial fictício, explicar os limites do "
        "protótipo ou encerrar a conversa. O que deseja simular?",
    ),
    "ajuda": (
        "Ajuda",
        "Descreva um cenário fictício com o que foi sentido, há quanto tempo e a "
        "intensidade. Eu apenas organizarei o relato; não farei avaliação médica.",
    ),
    "relatar_sintoma": (
        "Relatar sintoma fictício",
        "Entendi o relato fictício. Informe, se souber, há quanto tempo ocorreu e "
        "como você descreveria a intensidade. Depois confirme se o registro está "
        "correto.",
    ),
    "confirmar": (
        "Confirmar relato fictício",
        "Registro fictício confirmado. Ele serve apenas para demonstrar organização "
        "conversacional e não constitui avaliação médica.",
    ),
    "negar": (
        "Corrigir relato fictício",
        "Sem problema. Escreva novamente apenas a informação fictícia que deseja "
        "registrar.",
    ),
    "encerrar": (
        "Encerrar conversa",
        "Conversa encerrada. Este protótipo não substitui orientação profissional. "
        "Em urgência no Brasil, procure um serviço de emergência ou ligue 192.",
    ),
    "sinal_urgencia": (
        "Sinal de urgência",
        "Isso pode representar uma urgência. No Brasil, ligue agora para o SAMU 192 "
        "ou procure imediatamente um serviço de emergência. Não espere uma resposta "
        "deste protótipo.",
    ),
}

WELCOME = (
    "Olá! Sou o CardioIA, um protótipo acadêmico. Use apenas informações "
    "fictícias. Não faço diagnóstico nem prescrição. Como posso ajudar no cenário "
    "simulado?"
)
FALLBACK = (
    "Não consegui relacionar a mensagem ao fluxo acadêmico. Tente escrever "
    "'ajuda', relatar um cenário fictício ou digitar 'encerrar'."
)


def text_step(variable: str, text: str) -> dict:
    return {
        "step": variable,
        "type": "standard",
        "output": {
            "generic": [
                {
                    "values": [{"text": text}],
                    "response_type": "text",
                    "selection_policy": "sequential",
                }
            ]
        },
        "handlers": [],
        "resolver": {"type": "end_action"},
        "variable": variable,
    }


def custom_action(action_id: str, title: str, response: str) -> dict:
    variable = f"{action_id}_response"
    return {
        "type": "standard",
        "steps": [text_step(variable, response)],
        "title": title,
        "action": action_id,
        "boosts": [],
        "handlers": [],
        "condition": {"intent": action_id},
        "variables": [{"variable": variable, "data_type": "any"}],
    }


def replace_builtin(action: dict, text: str) -> None:
    variable = f"{action['action']}_response"
    action["steps"] = [text_step(variable, text)]
    action["variables"] = [{"variable": variable, "data_type": "any"}]


def main() -> int:
    exported = json.loads(EXPORT_PATH.read_text(encoding="utf-8"))
    v1_spec = json.loads(V1_SPEC_PATH.read_text(encoding="utf-8"))
    payload = deepcopy(exported)
    action_skill = next(
        skill for skill in payload["assistant_skills"] if skill.get("type") == "action"
    )
    workspace = action_skill["workspace"]

    builtins = {item["action"]: item for item in workspace.get("actions", [])}
    replace_builtin(builtins["welcome"], WELCOME)
    replace_builtin(builtins["anything_else"], FALLBACK)
    replace_builtin(builtins["fallback"], FALLBACK)

    priority = [
        "sinal_urgencia",
        "saudacao",
        "ajuda",
        "relatar_sintoma",
        "confirmar",
        "negar",
        "encerrar",
    ]
    custom_actions = {
        action_id: custom_action(action_id, *RESPONSES[action_id])
        for action_id in priority
    }
    ordered_actions = [builtins["welcome"]]
    ordered_actions.extend(custom_actions[action_id] for action_id in priority)
    ordered_actions.extend(
        [builtins["fallback"], builtins["run_always"], builtins["anything_else"]]
    )
    for current, following in zip(ordered_actions, ordered_actions[1:]):
        current["next_action"] = following["action"]
    ordered_actions[-1].pop("next_action", None)
    workspace["actions"] = ordered_actions

    legacy_intents = deepcopy(v1_spec["intents"])
    retained_intents = [
        intent
        for intent in workspace.get("intents", [])
        if intent.get("intent") == "fallback_connect_to_agent"
    ]
    workspace["intents"] = retained_intents + legacy_intents

    retained_entities = [
        entity
        for entity in workspace.get("entities", [])
        if entity.get("entity") in {"danger_words", "profane_words", "sys-yes-no"}
    ]
    workspace["entities"] = retained_entities + deepcopy(v1_spec["entities"])
    workspace["counterexamples"] = deepcopy(v1_spec.get("counterexamples", []))
    workspace.setdefault("metadata", {})["cardioia_version"] = "2.0.0-actions"
    settings = workspace.setdefault("system_settings", {})
    settings.setdefault("auto_learn", {})["apply"] = False
    settings.setdefault("disambiguation", {})["enabled"] = False

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "payload": "generated",
                "custom_actions": len(custom_actions),
                "training_examples": sum(
                    len(intent.get("examples", [])) for intent in legacy_intents
                ),
                "entities": len(v1_spec["entities"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
