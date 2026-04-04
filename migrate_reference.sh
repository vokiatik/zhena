#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/backend"

echo "Running migrations for REFERENCE database..."
alembic -c alembic_reference.ini upgrade head
echo "Reference database is up to date."
