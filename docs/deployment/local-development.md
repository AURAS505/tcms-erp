# Local Development

## Prerequisites

- Docker
- Docker Compose

## Start Services

```bash
cp .env.example .env
docker compose up --build
```

## URLs

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000/api/health/
- Django admin: http://localhost:8000/admin/

## Notes

The Step 1 skeleton has no production business modules or database migrations beyond Django defaults.
