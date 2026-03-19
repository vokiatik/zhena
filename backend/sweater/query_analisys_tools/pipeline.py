import concurrent.futures

import httpx

from sweater.query_analisys_tools.config import (
    ENTITY_MATCH_THRESHOLD,
    ENTITY_MATCH_TOP_K,
    VECTOR_DB_URL,
)
from sweater.query_analisys_tools.entity_extractor import extract_entities
from sweater.query_analisys_tools.query_decomposer import decompose_query
from sweater.query_analisys_tools.clarification import build_clarification_message

# Map entity labels from GLiNER to Qdrant collection names
LABEL_TO_COLLECTION = {
    "metric": "metrics",
}


# ── Core helpers ─────────────────────────────────────────────────────

def extract_and_match(text):
    """Extract entities from text and match them against the vector DB."""
    entities = extract_entities(text)
    matched, unmatched = match_entities(entities)
    return matched, unmatched


def search_vector_db(collection_name, query_text, limit=ENTITY_MATCH_TOP_K):
    """Call the vector DB HTTP API to search for similar entries."""
    response = httpx.get(
        f"{VECTOR_DB_URL}/search/{collection_name}",
        params={"q": query_text, "limit": limit},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def find_closest_match(collection_name, query_text):
    """Search the vector DB for the closest match to the given text.

    Returns (best_result, True) if score >= threshold, else (top_k_results, False).
    """
    results = search_vector_db(collection_name, query_text)

    best = results[0] if results else None
    if best is not None and best["score"] >= ENTITY_MATCH_THRESHOLD:
        return best, True
    return results, False


def match_entities(entities):
    """Match extracted entities against the vector DB.

    Returns (matched, unmatched) where:
      - matched: entities that found a high-confidence DB entry
      - unmatched: entities with only low-confidence candidates
    """
    matched = []
    unmatched = []
    for entity in entities:
        collection = LABEL_TO_COLLECTION.get(entity["label"], entity["label"])
        result, is_match = find_closest_match(collection, entity["text"])
        if is_match:
            matched.append({
                "text": result["payload"]["text"],
                "label": entity["label"],
            })
        else:
            closest_options = [
                {"text": r["payload"]["text"], "score": r["score"]}
                for r in result
            ] if result else []
            unmatched.append({
                "text": entity["text"],
                "label": entity["label"],
                "closest_options": closest_options,
            })
    return matched, unmatched


# ── Parallel execution ──────────────────────────────────────────────

def analyze_query(text):
    """Run entity extraction/matching and LLM decomposition in parallel."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        extraction_future = executor.submit(extract_and_match, text)
        decomposer_future = executor.submit(decompose_query, text)

        matched, unmatched = extraction_future.result()
        decomposed = decomposer_future.result()

    return matched, unmatched, decomposed


# ── Metric comparison ───────────────────────────────────────────────

def compare_metrics(matched_entities, decomposed_result):
    """Check if both agents extracted the same metric values."""
    embedding_metrics = {
        e["text"].lower() for e in matched_entities if e["label"] == "metric"
    }
    decomposed_metrics = {
        m.lower() for m in decomposed_result.get("metrics", [])
    }
    return embedding_metrics == decomposed_metrics


# ── Main processing pipeline ────────────────────────────────────────

def process_query(text):
    """Main entry point: runs parallel analysis, compares metrics, and
    returns either a ready result or a clarification request."""
    matched, unmatched, decomposed = analyze_query(text)
    metrics_match = compare_metrics(matched, decomposed)

    if not unmatched:
        return {
            "status": "ready",
            "result": build_sql_query(matched, decomposed),
            "metrics_match": metrics_match,
            "decomposed": decomposed,
        }

    message = build_clarification_message(unmatched)
    return {
        "status": "clarification_needed",
        "message": message,
        "unmatched": unmatched,
        "matched": matched,
        "decomposed": decomposed,
        "metrics_match": metrics_match,
    }


# ── Stub (to be implemented) ────────────────────────────────────────

def build_sql_query(matched_entities, decomposed_result):
    """Transform matched data into a SQL query."""
    return {
        "matched_entities": matched_entities,
        "decomposed_result": decomposed_result,
    }
