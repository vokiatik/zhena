from model_loader import load_model
from querries import text_eng, text_rus
from query_separator import query_separator

from vector_db import client
from qdrant_client.models import models


model_name = "google/embeddinggemma-300m"
model = load_model(model_name)

def run_analysis(text):
    entries = query_separator(text)
    print(entries)

    query_embeddings = get_query_embeddings(entries)
    print(query_embeddings)
    return query_embeddings

def get_vector_for_text(text):
    embedding = model.encode(
        [text],
        normalize_embeddings=True
    )
    return embedding

def get_query_embeddings(entries):
    for entry in entries:
        text = entry["text"]
        vector = get_vector_for_text(text)
        print(f"Text: {text}, Vector shape: {vector.shape}")
        if entry["label"] == "metric":
            return get_metric_db_hits(vector)
        elif entry["label"] == "brand":
            return get_brand_db_hits(vector)

def get_metric_db_hits(query_vector):
    results = client.query_points(
        collection_name="metrics",
        query=query_vector.flatten().tolist(),
        limit=3
    )

    for point in results.points:
        print(point.payload["text"], point.score)
    
    return results.points

def get_brand_db_hits(query_vector):
    results = client.query_points(
        collection_name="entities",
        query=query_vector.flatten().tolist(),
        limit=3
    )

    for point in results.points:
        print(point.payload["text"], point.score)
    
    return results.points