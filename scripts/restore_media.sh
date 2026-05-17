#!/usr/bin/env bash
set -euo pipefail

backup_file="${1:-}"
if [[ -z "${backup_file}" ]]; then
  echo "Usage: $0 <media-backup.tar.gz>" >&2
  exit 1
fi

if [[ ! -f "${backup_file}" ]]; then
  echo "Backup file does not exist: ${backup_file}" >&2
  exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
  echo "tar is required but was not found in PATH." >&2
  exit 1
fi

media_root="${MEDIA_ROOT:-${DJANGO_MEDIA_ROOT:-}}"
private_media_root="${PRIVATE_MEDIA_ROOT:-${DJANGO_PRIVATE_MEDIA_ROOT:-}}"

if [[ -z "${media_root}" && -z "${private_media_root}" ]]; then
  echo "Set MEDIA_ROOT/DJANGO_MEDIA_ROOT and/or PRIVATE_MEDIA_ROOT/DJANGO_PRIVATE_MEDIA_ROOT before restore." >&2
  exit 1
fi

echo "WARNING: restoring ${backup_file} will overwrite files in configured media directories." >&2
if [[ "${RESTORE_CONFIRM:-no}" != "yes" ]]; then
  read -r -p "Type RESTORE to continue: " confirmation
  if [[ "${confirmation}" != "RESTORE" ]]; then
    echo "Restore cancelled." >&2
    exit 1
  fi
fi

staging_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${staging_dir}"
}
trap cleanup EXIT

tar -xzf "${backup_file}" -C "${staging_dir}"

if [[ -n "${media_root}" && -d "${staging_dir}/media" ]]; then
  mkdir -p "${media_root}"
  cp -a "${staging_dir}/media/." "${media_root}/"
fi

if [[ -n "${private_media_root}" && -d "${staging_dir}/private_media" ]]; then
  mkdir -p "${private_media_root}"
  cp -a "${staging_dir}/private_media/." "${private_media_root}/"
fi

echo "Media restore completed from: ${backup_file}"
