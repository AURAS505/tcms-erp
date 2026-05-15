# API Conventions

All APIs should use consistent response envelopes.

Successful response:

```json
{
  "success": true,
  "data": {},
  "message": "",
  "errors": null,
  "meta": {}
}
```

Validation response:

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["error message"]
  }
}
```

Step 1 only exposes `GET /api/health/` for local infrastructure verification.
