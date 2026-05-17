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

backup_file="${1:-}"
if [[ -z "${backup_file}" ]]; then
  echo "Usage: $0 <backup-file.dump|backup-file.sql>" >&2
  exit 1
fi

if [[ ! -f "${backup_file}" ]]; then
  echo "Backup file does not exist: ${backup_file}" >&2
  exit 1
fi

echo "WARNING: restoring ${backup_file} will overwrite or change database '${POSTGRES_DB}' on ${POSTGRES_HOST}:${POSTGRES_PORT}." >&2
if [[ "${RESTORE_CONFIRM:-no}" != "yes" ]]; then
  read -r -p "Type RESTORE to continue: " confirmation
  if [[ "${confirmation}" != "RESTORE" ]]; then
    echo "Restore cancelled." >&2
    exit 1
  fi
fi

export PGPASSWORD="${POSTGRES_PASSWORD}"
trap 'unset PGPASSWORD' EXIT

case "${backup_file}" in
  *.dump|*.backup)
    if ! command -v pg_restore >/dev/null 2>&1; then
      echo "pg_restore is required for custom-format backups but was not found in PATH." >&2
      exit 1
    fi
    pg_restore \
      --host="${POSTGRES_HOST}" \
      --port="${POSTGRES_PORT}" \
      --username="${POSTGRES_USER}" \
      --dbname="${POSTGRES_DB}" \
      --clean \
      --if-exists \
      --no-owner \
      --no-password \
      "${backup_file}"
    ;;
  *.sql)
    if ! command -v psql >/dev/null 2>&1; then
      echo "psql is required for SQL backups but was not found in PATH." >&2
      exit 1
    fi
    psql \
      --host="${POSTGRES_HOST}" \
      --port="${POSTGRES_PORT}" \
      --username="${POSTGRES_USER}" \
      --dbname="${POSTGRES_DB}" \
      --no-password \
      --file="${backup_file}"
    ;;
  *)
    echo "Unsupported backup file extension. Expected .dump, .backup, or .sql." >&2
    exit 1
    ;;
esac

echo "PostgreSQL restore completed from: ${backup_file}"
