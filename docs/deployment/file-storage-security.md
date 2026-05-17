# File Storage Security

TCMS ERP currently stores document references as path metadata. Full upload endpoints and frontend upload screens are intentionally pending, but backend validation utilities and storage settings are available for future upload implementations.

## Validation Baseline

Use the common validators in `apps/backend/common/validators.py` before accepting uploaded documents:

- Allowed extensions default to `pdf`, `jpg`, `jpeg`, `png`, `doc`, and `docx`.
- Maximum upload size defaults to 2 MB, matching the current SOP target for student and admission documents.
- Safe storage paths use randomized UUID filenames and do not trust the original filename.
- Validation errors are explicit and suitable for API responses.

Extension checks are a baseline only. A production upload endpoint should also verify content type and, where practical, inspect file signatures before persistence. No heavy MIME detection or antivirus dependency is added in this step.

## Environment Settings

Local development defaults:

```env
DJANGO_MEDIA_ROOT=/app/media
DJANGO_MEDIA_URL=/media/
DJANGO_PRIVATE_MEDIA_ROOT=/app/private_media
DJANGO_DEFAULT_FILE_STORAGE=django.core.files.storage.FileSystemStorage
DJANGO_MAX_UPLOAD_SIZE_BYTES=2097152
DJANGO_ALLOWED_UPLOAD_EXTENSIONS=pdf,jpg,jpeg,png,doc,docx
```

Production should keep sensitive documents outside any public static/media directory. Reverse proxies must not expose `DJANGO_PRIVATE_MEDIA_ROOT` directly.

## Private Media Principle

Student documents, financial documents, payroll acknowledgements, and accounting support documents should be treated as private. Do not serve them through unauthenticated public media URLs. Future download endpoints should authorize the request, verify branch or organization scope, and stream or redirect to a short-lived private URL.

## S3-Compatible Readiness

Future S3-compatible storage should use private buckets, server-side encryption, no public ACLs, and short-lived signed URLs for authorized downloads. The current configuration keeps the storage backend environment-driven but does not add an S3 dependency.

## Pending Work

- Authenticated private file download endpoints.
- Optional signed URL support for S3-compatible storage.
- MIME/signature validation beyond extension allow-listing.
- Antivirus or malware scanning for uploaded files.
- Frontend upload screens.
