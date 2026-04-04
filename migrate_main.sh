#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/backend"

echo "Running migrations for MAIN database..."
alembic -c alembic_main.ini upgrade head
echo "Main database is up to date."
