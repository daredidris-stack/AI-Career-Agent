# Production deployment

Deploy the API and frontend as separate services with managed PostgreSQL. The repository includes production-style container images and a local Compose stack for repeatable validation.

## Release sequence

1. Build immutable images from a reviewed commit.
2. Inject secrets through the hosting provider; never copy `.env` into an image.
3. Back up the production database.
4. Run `alembic upgrade head` as a release task.
5. Start the API and wait for `/health/ready` to return 200.
6. Deploy the frontend with `VITE_API_URL` set to the public API origin.
7. Run authenticated smoke tests and monitor errors before completing the rollout.

The API container performs migration before startup for a single-instance deployment. Multi-instance platforms should run migration as a separate one-off release task to avoid concurrent migration attempts.

## Required production configuration

- `APP_ENV=production`
- `APP_RELEASE` set to the Git commit or release identifier
- a managed PostgreSQL `DATABASE_URL`
- a randomly generated `JWT_SECRET_KEY` stored in the platform secret manager
- exact HTTPS values for `FRONTEND_URL` and `CORS_ALLOWED_ORIGINS`
- SMTP credentials when verification is required
- approved job-provider credentials
- AI limits appropriate for the product plan

Rotate a leaked credential immediately and revoke it at its provider. JWT-secret rotation signs users out; schedule it and communicate when possible.

## Monitoring

- Poll `/health/live` for process liveness.
- Poll `/health/ready` for database and production-configuration readiness.
- Ingest JSON request logs and retain the `x-request-id` returned to clients.
- Alert on sustained 5xx responses, readiness failures, high latency, database saturation, migration failures, and AI-provider timeout rates.
- Logs intentionally exclude authorization headers, request bodies, resumes, job descriptions, email addresses, and URL query strings.

## Local container validation

Copy no secrets into the repository. The Compose credentials are explicitly local-only:

```bash
docker compose up --build
curl http://localhost:8000/health/ready
```

The local Ollama process is not bundled into the API image. Configure network access to an approved model provider separately before testing AI features in containers.
