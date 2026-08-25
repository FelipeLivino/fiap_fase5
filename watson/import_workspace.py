from __future__ import annotations

import json
import os
import time
from pathlib import Path

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV1


SPEC_PATH = Path("watson/assistant-export.json")


def client() -> AssistantV1:
    service = AssistantV1(
        version=os.getenv("WATSON_API_VERSION", "2024-08-25"),
        authenticator=IAMAuthenticator(os.environ["WATSON_API_KEY"]),
    )
    service.set_service_url(os.environ["WATSON_SERVICE_URL"])
    return service


def wait_until_ready(service: AssistantV1, workspace_id: str) -> str:
    status = "Training"
    for _ in range(24):
        workspace = service.get_workspace(workspace_id).get_result()
        status = str(workspace.get("status", "Unknown"))
        if status.casefold() in {"available", "failed"}:
            return status
        time.sleep(5)
    return status


def main() -> int:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    service = client()
    workspace_fields = {
        "name": spec.get("name"),
        "description": spec.get("description"),
        "language": spec.get("language"),
        "intents": spec.get("intents"),
        "entities": spec.get("entities"),
        "dialog_nodes": spec.get("dialog_nodes"),
        "counterexamples": spec.get("counterexamples"),
        "metadata": spec.get("metadata"),
        "system_settings": spec.get("system_settings"),
    }
    existing = service.list_workspaces(page_limit=100).get_result().get(
        "workspaces", []
    )
    match = next((item for item in existing if item.get("name") == spec["name"]), None)
    if match:
        workspace_id = match["workspace_id"]
        service.update_workspace(
            workspace_id=workspace_id,
            append=False,
            **workspace_fields,
        ).get_result()
        action = "updated"
    else:
        response = service.create_workspace(**workspace_fields).get_result()
        workspace_id = response["workspace_id"]
        action = "created"

    status = wait_until_ready(service, workspace_id)
    print(
        json.dumps(
            {
                "action": action,
                "workspace_id": workspace_id,
                "status": status,
            },
            ensure_ascii=False,
        )
    )
    return 0 if status.casefold() == "available" else 2


if __name__ == "__main__":
    raise SystemExit(main())
