#!/usr/bin/env bash
set -euo pipefail

# ─── Text Analyser – Development Startup Script ─────────────────
# Starts all infrastructure via Docker Compose, then runs the
# backend (FastAPI) and frontend (Vite) locally with hot-reload.
# ─────────────────────────────────────────────────────────────────

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ── Colours ──────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

# ── Cleanup on exit ─────────────────────────────────────────────
PIDS=()
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    for pid in "${PIDS[@]:-}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    echo -e "${GREEN}All local processes stopped.${NC}"
    echo -e "${YELLOW}Docker containers are still running. Stop them with:${NC}"
    echo -e "  docker compose down"
}
trap cleanup EXIT INT TERM

# ── Docker services to start/wait for ───────────────────────────
SERVICES=(
    postgres
    clickhouse
    duckling
    ollama
    ollama-pull
    vector_db
    mailhog
)

# ── Helpers ─────────────────────────────────────────────────────
get_container_id() {
    docker compose ps -q "$1"
}

wait_for_service() {
    local service="$1"
    local timeout="${2:-120}"
    local elapsed=0

    echo -e "${CYAN}Waiting for service '${service}'...${NC}"

    while [ "$elapsed" -lt "$timeout" ]; do
        local cid
        cid="$(get_container_id "$service")"

        if [ -n "$cid" ]; then
            local state
            state="$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null || echo "unknown")"

            local health
            health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || echo "unknown")"

            local exit_code
            exit_code="$(docker inspect -f '{{.State.ExitCode}}' "$cid" 2>/dev/null || echo "1")"

            # 1) Healthy container
            if [ "$health" = "healthy" ]; then
                echo -e "${GREEN}✓ ${service} is healthy${NC}"
                return 0
            fi

            # 2) No healthcheck, but running
            if [ "$health" = "none" ] && [ "$state" = "running" ]; then
                echo -e "${GREEN}✓ ${service} is running${NC}"
                return 0
            fi

            # 3) One-shot success container (e.g. ollama-pull)
            if [ "$state" = "exited" ] && [ "$exit_code" = "0" ]; then
                echo -e "${GREEN}✓ ${service} completed successfully${NC}"
                return 0
            fi

            # 4) Failed container
            if [ "$state" = "exited" ] && [ "$exit_code" != "0" ]; then
                echo -e "${RED}✗ ${service} exited with code ${exit_code}${NC}"
                docker compose logs --no-color "$service" || true
                exit 1
            fi
        fi

        sleep 2
        elapsed=$((elapsed + 2))
    done

    echo -e "${RED}✗ ${service} did not become ready in time${NC}"
    docker compose ps
    docker compose logs --no-color "$service" || true
    exit 1
}

# ── 1. Load .env ────────────────────────────────────────────────
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo -e "${GREEN}✓ Loaded .env${NC}"
else
    echo -e "${RED}✗ .env file not found – copy .env.example to .env and fill in values${NC}"
    exit 1
fi

# ── 2. Start Docker infrastructure ─────────────────────────────
echo -e "${CYAN}Starting Docker containers (postgres, clickhouse, duckling, ollama, ollama-pull, vector_db, mailhog)...${NC}"
docker compose up -d "${SERVICES[@]}"
echo -e "${GREEN}✓ Docker containers started${NC}"

# ── 3. Wait for all Docker services ────────────────────────────
echo -e "${CYAN}Waiting for all Docker services to be ready...${NC}"
for service in "${SERVICES[@]}"; do
    wait_for_service "$service" 180
done
echo -e "${GREEN}✓ All Docker services are up${NC}"

# ── 4. Extra Postgres readiness check ──────────────────────────
echo -e "${CYAN}Waiting for Postgres to accept connections...${NC}"
for i in $(seq 1 60); do
    if docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-app}" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Postgres is ready${NC}"
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo -e "${RED}✗ Postgres did not become ready in time${NC}"
        exit 1
    fi
    sleep 1
done

# ── 5. Activate Python venv & install backend deps ─────────────
if [ -d "venv" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
    echo -e "${GREEN}✓ Activated Python venv${NC}"
else
    echo -e "${RED}✗ Python venv not found. Create one first:${NC}"
    echo "  python3 -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt"
    exit 1
fi

# ── 6. Install frontend deps if needed ─────────────────────────
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${CYAN}Installing frontend dependencies...${NC}"
    (cd frontend && npm install)
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
fi

# ── 7. Run DB init ─────────────────────────────────────────────
echo -e "${CYAN}Running DB init...${NC}"
python db_init.py
echo -e "${GREEN}✓ DB init completed${NC}"

# ── 8. Run Alembic migrations ──────────────────────────────────
echo -e "${CYAN}Running Alembic migrations...${NC}"
(cd backend && alembic -c alembic_main.ini upgrade head)
(cd backend && alembic -c alembic_reference.ini upgrade head)
echo -e "${GREEN}✓ Database migrations applied${NC}"

# ── 9. Start backend (FastAPI with hot-reload) ─────────────────
echo -e "${CYAN}Starting backend on http://localhost:8001 ...${NC}"
(cd backend && uvicorn main:app --host 0.0.0.0 --port 8001 --reload) &
PIDS+=($!)

# ── 10. Start frontend (Vite dev server) ───────────────────────
echo -e "${CYAN}Starting frontend on http://localhost:5173 ...${NC}"
(cd frontend && npm run dev -- --host) &
PIDS+=($!)

# ── Ready ───────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Development environment is starting up!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "  Frontend:   ${CYAN}http://localhost:5173${NC}"
echo -e "  Backend:    ${CYAN}http://localhost:8001${NC}"
echo -e "  MailHog UI: ${CYAN}http://localhost:8025${NC}"
echo -e "  Postgres:   ${CYAN}localhost:5432${NC}"
echo -e "  ClickHouse: ${CYAN}localhost:8123${NC}"
echo -e "  Ollama:     ${CYAN}localhost:11434${NC}"
echo -e "  Vector DB:  ${CYAN}localhost:8002${NC}"
echo -e "  Duckling:   ${CYAN}localhost:8000${NC}"
echo ""
echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop backend & frontend."
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

# Keep script alive until Ctrl+C
wait