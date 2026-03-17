from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sweater.database import get_pool, close_pool
from sweater.migrations import run_migrations
from sweater.chat import router as chat_router
from sweater.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await get_pool()
    await run_migrations(pool)
    yield
    await close_pool()


app = FastAPI(title="Text Analyser API", lifespan=lifespan)

# Allow the Vite dev server origin (local + Docker)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "Text Analyser API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
