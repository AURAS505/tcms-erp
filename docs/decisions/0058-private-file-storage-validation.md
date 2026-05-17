# 0058 Private File Storage Validation

## Status

Accepted.

## Context

The current backend models store document paths as string metadata rather than Django `FileField` uploads. Student, billing, payroll, and accounting modules already reference sensitive documents, so upload validation and private storage expectations need to exist before real upload workflows are added.

## Decision

Add reusable backend validation utilities for future upload endpoints:

- extension allow-listing for `pdf`, `jpg`, `jpeg`, `png`, `doc`, and `docx`
- default 2 MB maximum upload size
- safe randomized upload paths that do not trust original filenames
- environment-driven media and private media settings

No model fields were changed because the current file references are placeholders. This avoids unnecessary migrations and keeps this step focused on hardening guidance.

## Security Notes

The backend must remain the authority for upload validation. Original filenames are display metadata only and must not be used as storage paths. Sensitive documents should be stored privately and served only through authenticated, branch- or organization-scoped access.

## Limitations

This step does not add upload APIs, frontend upload UI, MIME signature inspection, antivirus scanning, signed URLs, or an S3 dependency. Those remain future production-readiness work.
