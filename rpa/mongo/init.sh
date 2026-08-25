#!/usr/bin/env bash
set -Eeuo pipefail

: "${RPA_MONGO_PASSWORD:?RPA_MONGO_PASSWORD ausente}"

worker_password_json="$(printf '%s' "$RPA_MONGO_PASSWORD" | jq -Rs .)"
{
  printf 'const workerPassword = %s;\n' "$worker_password_json"
  sed -n '1,$p' /docker-entrypoint-initdb.d/10-cardioia.js.tpl
} | "${mongo[@]}" "$MONGO_INITDB_DATABASE"
unset worker_password_json
