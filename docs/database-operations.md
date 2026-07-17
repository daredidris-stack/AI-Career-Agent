# Database operations

Production deployments should use PostgreSQL and run schema migrations before starting the API. SQLite remains available for local development only.

## New database

Set `DATABASE_URL` to a PostgreSQL connection string, then run:

```bash
alembic upgrade head
```

Hosted URLs beginning with either `postgres://` or `postgresql://` are automatically configured to use the Psycopg 3 driver.

## Existing database adoption

The first migration represents the schema already used by the application. Back up an existing database, verify that its tables match the models, and mark it as current once:

```bash
alembic stamp 20260717_0001
```

Do not run `stamp` on an empty database because it records a version without creating tables.

## PostgreSQL backup

Create an encrypted, access-controlled backup before every migration and at least daily:

```bash
pg_dump --format=custom --no-owner --no-acl "$DATABASE_URL" --file career-agent.dump
pg_restore --list career-agent.dump
```

Store backups outside the application host, encrypt them at rest, restrict access, and apply the same retention policy as other customer data.

## PostgreSQL restore drill

Restore into a separate empty database; never test a restore against production:

```bash
createdb career_agent_restore_test
pg_restore --exit-on-error --no-owner --no-acl --dbname career_agent_restore_test career-agent.dump
DATABASE_URL="postgresql://localhost/career_agent_restore_test" alembic current
```

Verify user counts, profiles, documents, analyses, and applications, then run API smoke tests. A backup is not considered reliable until a restore drill succeeds. Record the backup timestamp, migration revision, restore duration, and verification result.

## SQLite local backup

Stop the API before copying the local database so no write is in progress:

```bash
sqlite3 career_agent.db ".backup 'career_agent.backup.db'"
sqlite3 career_agent.backup.db "PRAGMA integrity_check;"
```

Restore by keeping the damaged database for investigation and placing a verified backup at the configured SQLite path.

## Rollback policy

Prefer a forward corrective migration. Before a risky migration, test both upgrade and downgrade on a recent restored backup. Application deployment should stop if `alembic upgrade head` fails; it must not start against a partially migrated schema.
