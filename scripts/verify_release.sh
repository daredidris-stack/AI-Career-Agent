#!/bin/sh
set -eu

REPOSITORY_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VERIFY_TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/nexthire-release.XXXXXX")
trap 'rm -rf "$VERIFY_TMP_DIR"' EXIT

cd "$REPOSITORY_ROOT"

: "${JWT_SECRET_KEY:=release-verification-secret}"
export JWT_SECRET_KEY

.venv/bin/python -W error::ResourceWarning -m unittest discover -s tests

DATABASE_URL="sqlite:///$VERIFY_TMP_DIR/migration.db" .venv/bin/alembic upgrade head
DATABASE_URL="sqlite:///$VERIFY_TMP_DIR/migration.db" .venv/bin/alembic check
DATABASE_URL="sqlite:///$VERIFY_TMP_DIR/migration.db" .venv/bin/alembic downgrade base
DATABASE_URL="sqlite:///$VERIFY_TMP_DIR/migration.db" .venv/bin/alembic upgrade head

(cd frontend && npm run lint && npm run build)

git diff --check
echo "Release verification passed."
