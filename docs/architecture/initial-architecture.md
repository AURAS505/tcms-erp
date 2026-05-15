# Initial Architecture

TCMS ERP is structured as a monorepo with separate backend and frontend applications.

## Backend

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery worker and beat

The backend currently contains app placeholders only. Business models, permissions, service-layer logic, financial posting, and migrations are intentionally deferred.

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- TanStack Query, React Hook Form, and Zod planned for application work

The frontend currently contains a minimal landing route for local development verification only.

## Infrastructure

- Docker Compose runs PostgreSQL, Redis, backend, Celery worker, Celery beat, and frontend.
- `.env.example` contains local defaults only and must not be used as production secrets.
