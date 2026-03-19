from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from qdrant_client.models import PointStruct

from vector_db import client, model
from seed_data import metric_example_db


def seed_db():
    metrics_count = client.count(collection_name="metrics").count

    if metrics_count == 0:
        print("Upserting metrics into Qdrant...")
        for i, metric in enumerate(metric_example_db):
            vector = model.encode([metric["metric_name"]], normalize_embeddings=True)[0]
            client.upsert(
                collection_name="metrics",
                points=[
                    PointStruct(
                        id=i,
                        vector=vector.tolist(),
                        payload={
                            "text": metric["metric_name"],
                            "description": metric["description"],
                            "sql_snippet": metric["sql_snippet"],
                        },
                    )
                ],
            )
    else:
        print(f"Metrics already seeded ({metrics_count} points), skipping.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_db()
    print("Vector DB ready")
    yield


app = FastAPI(title="Vector DB Service", lifespan=lifespan)


@app.get("/health")
async def health():
    collections = client.get_collections().collections
    return {"status": "ok", "collections": [c.name for c in collections]}


@app.get("/search/{collection}")
async def search(
    collection: str,
    q: str = Query(..., description="search query text"),
    limit: int = Query(5, ge=1, le=50),
):
    vector = model.encode([q], normalize_embeddings=True)[0].tolist()
    results = client.query_points(
        collection_name=collection,
        query=vector,
        limit=limit,
    )
    return [
        {"score": r.score, "payload": r.payload}
        for r in results.points
    ]
