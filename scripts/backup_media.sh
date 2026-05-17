#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${BACKUP_DIR:-}" ]]; then
  echo "Missing required environment variable: BACKUP_DIR" >&2
  exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
  echo "tar is required but was not found in PATH." >&2
  exit 1
fi

media_root="${MEDIA_ROOT:-${DJANGO_MEDIA_ROOT:-}}"
private_media_root="${PRIVATE_MEDIA_ROOT:-${DJANGO_PRIVATE_MEDIA_ROOT:-}}"

timestamp="$(date -u +"%Y%m%dT%H%M%SZ")"
backup_dir="${BACKUP_DIR%/}/media"
backup_file="${backup_dir}/media_${timestamp}.tar.gz"
staging_dir="$(mktemp -d)"

cleanup() {
  rm -rf "${staging_dir}"
}
trap cleanup EXIT

mkdir -p "${backup_dir}"

copied_any=false
if [[ -n "${media_root}" && -d "${media_root}" ]]; then
  mkdir -p "${staging_dir}/media"
  cp -a "${media_root}/." "${staging_dir}/media/"
  copied_any=true
fi

if [[ -n "${private_media_root}" && -d "${private_media_root}" ]]; then
  mkdir -p "${staging_dir}/private_media"
  cp -a "${private_media_root}/." "${staging_dir}/private_media/"
  copied_any=true
fi

if [[ "${copied_any}" != "true" ]]; then
  echo "No media directories found. Set MEDIA_ROOT/DJANGO_MEDIA_ROOT and/or PRIVATE_MEDIA_ROOT/DJANGO_PRIVATE_MEDIA_ROOT." >&2
  exit 1
fi

tar -czf "${backup_file}" -C "${staging_dir}" .

if [[ -n "${BACKUP_RETENTION_DAYS:-}" ]]; then
  find "${backup_dir}" -type f -name "media_*.tar.gz" -mtime +"${BACKUP_RETENTION_DAYS}" -delete
fi

echo "Media backup created: ${backup_file}"
