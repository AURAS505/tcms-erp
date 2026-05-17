#!/usr/bin/env bash
set -euo pipefail

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required environment variable: ${name}" >&2
    exit 1
  fi
}

require_env POSTGRES_HOST
require_env POSTGRES_PORT
require_env POSTGRES_DB
require_env POSTGRES_USER
require_env POSTGRES_PASSWORD
require_env BACKUP_DIR

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump is required but was not found in PATH." >&2
  exit 1
fi

timestamp="$(date -u +"%Y%m%dT%H%M%SZ")"
backup_dir="${BACKUP_DIR%/}/postgres"
backup_file="${backup_dir}/${POSTGRES_DB}_${timestamp}.dump"

mkdir -p "${backup_dir}"

export PGPASSWORD="${POSTGRES_PASSWORD}"
trap 'unset PGPASSWORD' EXIT

pg_dump \
  --host="${POSTGRES_HOST}" \
  --port="${POSTGRES_PORT}" \
  --username="${POSTGRES_USER}" \
  --dbname="${POSTGRES_DB}" \
  --format=custom \
  --file="${backup_file}" \
  --no-password

if [[ -n "${BACKUP_RETENTION_DAYS:-}" ]]; then
  find "${backup_dir}" -type f -name "${POSTGRES_DB}_*.dump" -mtime +"${BACKUP_RETENTION_DAYS}" -delete
fi

echo "PostgreSQL backup created: ${backup_file}"
