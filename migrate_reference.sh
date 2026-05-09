#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "Running migrations for REFERENCE database..."

VENV_ALEMBIC="$SCRIPT_DIR/venv/bin/alembic"
if [ -x "$VENV_ALEMBIC" ]; then
  "$VENV_ALEMBIC" -c alembic_reference.ini upgrade head
else
  alembic -c alembic_reference.ini upgrade head
fi
echo "Reference database is up to date."
