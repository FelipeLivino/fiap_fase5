from __future__ import annotations

import json
import os
import time
from pathlib import Path

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2
from ibm_watson.assistant_v2 import AssistantState, SkillImport


def client() -> AssistantV2:
    key_file = Path(os.getenv("WATSON_API_KEY_FILE", "/run/secrets/watson_api_key"))
    service = AssistantV2(
        version=os.getenv("WATSON_API_VERSION", "2024-08-25"),
        authenticator=IAMAuthenticator(key_file.read_text(encoding="utf-8").strip()),
    )
    service.set_service_url(os.environ["WATSON_SERVICE_URL"])
    return service


def main() -> int:
    assistant_id = os.environ["WATSON_ASSISTANT_ID"]
    payload_path = Path(os.getenv("SKILLS_IMPORT_PATH", "/export/actions-import.json"))
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    skills = [SkillImport.from_dict(item) for item in payload["assistant_skills"]]
    state = AssistantState.from_dict(payload["assistant_state"])
    service = client()

    if os.getenv("IMPORT_STATUS_ONLY", "0") == "1":
        initial = service.import_skills_status(assistant_id=assistant_id).get_result()
    else:
        initial = service.import_skills(
            assistant_id=assistant_id,
            assistant_skills=skills,
            assistant_state=state,
            include_audit=False,
        ).get_result()
    status_result = initial
    status = str(initial.get("status", "Processing"))

    success_statuses = {"available", "completed"}
    for _ in range(36):
        if status.casefold() in success_statuses | {"failed"}:
            break
        time.sleep(5)
        status_result = service.import_skills_status(
            assistant_id=assistant_id
        ).get_result()
        status = str(status_result.get("status", "Unknown"))

    summary = {
        "import": "completed" if status.casefold() in success_statuses else "failed",
        "status": status,
    }
    if status.casefold() == "failed":
        summary["status_description"] = status_result.get("status_description")
        summary["status_errors"] = status_result.get("status_errors", [])
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if status.casefold() in success_statuses else 2


if __name__ == "__main__":
    raise SystemExit(main())
