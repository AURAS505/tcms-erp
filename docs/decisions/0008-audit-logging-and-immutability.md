# 0008 Audit Logging and Financial Immutability

## Decision

Add centralized audit logging in the `common` app and foundational immutability controls for posted accounting records.

## Audit Log Design

`AuditLog` is shared infrastructure. It stores optional organization, branch, user, action, module, object identity, before/after JSON payloads, metadata, reason, IP address, user agent, request ID, and creation timestamp.

The audit service can be called by future accounting, billing, payroll, authentication, academic rollover, and administrative workflows. It also reads the existing request audit context placeholder so future middleware can attach user/request metadata consistently.

## Append-Only Principle

Audit logs are append-only. The model blocks normal instance updates and deletes. Django admin exposes audit logs as read-only and disables add/change/delete actions for normal admin use.

## Immutable Financial Record Control

Posted, reversed, and void journal entries are protected from normal `save()` and `delete()` calls. Their lines are also protected from normal edits and deletion. This is the first enforcement layer for the rule that posted financial records cannot be edited or deleted.

## Reversal Over Edit/Delete

Accounting corrections must preserve the audit trail. Future correction workflows must create reversal entries and then repost corrected entries instead of mutating posted data.

## What Is Not Implemented Yet

This step does not implement billing, payroll, student payments, teacher payments, approval workflows, accounting APIs, frontend pages, academic year rollover execution, bank reconciliation, tax calculation, or full reversal-entry generation.

## Status

Accepted.
