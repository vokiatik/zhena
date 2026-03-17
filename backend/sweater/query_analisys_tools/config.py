import os

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3:1.7b"

EMBEDDING_MODEL_NAME = "google/embeddinggemma-300m"
VECTOR_DB_URL = os.environ.get("VECTOR_DB_URL", "http://localhost:8002")

ENTITY_MATCH_THRESHOLD = 0.85
ENTITY_MATCH_TOP_K = 3
