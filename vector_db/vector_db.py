import os

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

model_name = "google/embeddinggemma-300m"
model = SentenceTransformer(model_name)

DB_PATH = os.environ.get("QDRANT_DB_PATH", os.path.join(os.path.dirname(__file__), "db_dump"))
os.makedirs(DB_PATH, exist_ok=True)

client = QdrantClient(path=DB_PATH)

COLLECTIONS = ["metrics", "synonyms"]

existing = {c.name for c in client.get_collections().collections}
for name in COLLECTIONS:
    if name not in existing:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
