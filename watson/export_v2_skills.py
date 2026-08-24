from __future__ import annotations

import json
import os
import time
from pathlib import Path

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2


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
    output_path = Path(os.getenv("SKILLS_EXPORT_PATH", "/export/skills.json"))
    service = client()
    result: dict = {}

    for attempt in range(24):
        result = service.export_skills(
            assistant_id=assistant_id,
            include_audit=False,
        ).get_result()
        status = str(result.get("status", "Unknown"))
        if result.get("assistant_skills") or status.casefold() == "failed":
            break
        time.sleep(5)

    status = str(result.get("status", "Unknown"))
    if status.casefold() == "failed" or not result.get("assistant_skills"):
        print(json.dumps({"status": status, "exported": False}, ensure_ascii=False))
        return 2

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    skill_types = [item.get("type", "unknown") for item in result["assistant_skills"]]
    print(
        json.dumps(
            {
                "status": status,
                "exported": True,
                "skill_count": len(skill_types),
                "skill_types": skill_types,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
