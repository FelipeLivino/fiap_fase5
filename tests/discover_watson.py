from __future__ import annotations

import json
import os
from pathlib import Path

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_watson import AssistantV1, AssistantV2


def main() -> int:
    api_key_file = Path(
        os.getenv("WATSON_API_KEY_FILE", "/run/secrets/watson_api_key")
    )
    api_key = api_key_file.read_text(encoding="utf-8").strip()
    service_url = os.environ["WATSON_SERVICE_URL"]
    version = os.getenv("WATSON_API_VERSION", "2024-08-25")

    assistant = AssistantV2(
        version=version,
        authenticator=IAMAuthenticator(api_key),
    )
    assistant.set_service_url(service_url)
    try:
        result = assistant.list_assistants(
            page_limit=100,
            include_count=True,
        ).get_result()
    except ApiException as exc:
        if exc.code != 400:
            raise
        classic = AssistantV1(
            version=version,
            authenticator=IAMAuthenticator(api_key),
        )
        classic.set_service_url(service_url)
        workspaces = classic.list_workspaces(
            page_limit=100,
            include_count=True,
        ).get_result()
        sanitized = [
            {
                "name": workspace.get("name"),
                "workspace_id": workspace.get("workspace_id"),
                "language": workspace.get("language"),
            }
            for workspace in workspaces.get("workspaces", [])
        ]
        print(
            json.dumps(
                {
                    "v2_listing": "unsupported_by_plan",
                    "classic_workspaces": sanitized,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if sanitized else 2

    assistants = []
    for item in result.get("assistants", []):
        environments = [
            {
                "name": environment.get("name"),
                "environment": environment.get("environment"),
                "environment_id": environment.get("environment_id"),
            }
            for environment in item.get("assistant_environments", [])
        ]
        assistants.append(
            {
                "name": item.get("name"),
                "assistant_id": item.get("assistant_id"),
                "environments": environments,
            }
        )

    print(json.dumps({"assistants": assistants}, ensure_ascii=False, indent=2))
    return 0 if assistants else 2


if __name__ == "__main__":
    raise SystemExit(main())
