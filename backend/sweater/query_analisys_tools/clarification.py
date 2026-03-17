import json

import requests

from sweater.query_analisys_tools.config import OLLAMA_URL, OLLAMA_MODEL


def build_clarification_message(unmatched_entities):
    """Build a user-facing message listing unknown values and their closest
    database matches so the user can verify or correct them."""
    lines = [
        "There is no exact value in the database for the following entries. "
        "Those are the closest matches. Please verify if any of them are correct. "
        "If not, please provide information for this value or how to describe it.\n"
    ]

    for entry in unmatched_entities:
        lines.append(f'• "{entry["text"]}" (category: {entry["label"]}):')
        if entry.get("closest_options"):
            for i, option in enumerate(entry["closest_options"], 1):
                lines.append(
                    f"    {i}. {option['text']} (similarity: {option['score']:.2f})"
                )
        else:
            lines.append("    No close matches found.")
        lines.append("")

    return "\n".join(lines)


def parse_user_clarification(user_response, unmatched_entry):
    """Use LLM to determine whether the user confirmed one of the listed
    options or provided a brand-new explanation for the value."""
    closest_texts = [
        opt["text"] for opt in unmatched_entry.get("closest_options", [])
    ]

    prompt = (
        f'The user was asked to clarify the value "{unmatched_entry["text"]}" '
        f'(category: {unmatched_entry["label"]}).\n'
        f"The closest existing options were: {json.dumps(closest_texts)}\n\n"
        f'The user responded: "{user_response}"\n\n'
        "Determine if the user:\n"
        "1. CONFIRMED one of the listed options (responded with the name or number of an option)\n"
        "2. PROVIDED a new explanation/description of the value\n\n"
        "Respond ONLY with JSON:\n"
        '{"action": "confirmed", "confirmed_value": "<the option text>"}\n'
        "or\n"
        '{"action": "new_explanation", "explanation": "<user\'s explanation>"}\n'
    )

    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_predict": 256},
        "format": "json",
    })
    response.raise_for_status()
    raw = response.json()["message"]["content"].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"action": "new_explanation", "explanation": user_response}


def transform_to_collection_entry(user_explanation, collection_name):
    """Call LLM to rewrite the user's free-text explanation into a structured
    entry that matches the schema of *collection_name*."""
    prompt = (
        f"Transform the following user description into a structured entry for "
        f'the "{collection_name}" collection.\n\n'
        f'User description: "{user_explanation}"\n\n'
        f'Return a JSON object with the fields appropriate for the "{collection_name}" '
        f'collection. The entry must include at minimum a "text" field with a canonical name.\n'
        "Respond ONLY with valid JSON."
    )

    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_predict": 512},
        "format": "json",
    })
    response.raise_for_status()
    raw = response.json()["message"]["content"].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"text": user_explanation}


def handle_clarification(user_response, unmatched_entry):
    """Process a single user clarification response.

    Returns a dict describing the next action:
      • {"status": "confirm_new_value", ...} → user gave a new explanation
      • {"status": "synonym_added", ...}     → user confirmed an existing option
    """
    parsed = parse_user_clarification(user_response, unmatched_entry)

    if parsed["action"] == "confirmed":
        confirmed_value = parsed["confirmed_value"]
        add_embedding_to_db(
            "synonyms",
            unmatched_entry["text"],
            {
                "text": unmatched_entry["text"],
                "canonical": confirmed_value,
                "label": unmatched_entry["label"],
            },
        )
        return {
            "status": "synonym_added",
            "original_text": unmatched_entry["text"],
            "confirmed_value": confirmed_value,
            "entry": unmatched_entry,
        }

    proposed = transform_to_collection_entry(
        parsed["explanation"], unmatched_entry["label"]
    )
    return {
        "status": "confirm_new_value",
        "proposed_entry": proposed,
        "entry": unmatched_entry,
        "message": (
            f"Based on your description, here is the proposed entry:\n"
            f"{json.dumps(proposed, indent=2)}\n\n"
            f"Is this correct? (yes/no)"
        ),
    }


def handle_new_value_confirmation(confirmed, proposed_entry, unmatched_entry):
    """Handle the user's yes/no answer to the LLM-generated entry."""
    if confirmed:
        add_embedding_to_db(
            unmatched_entry["label"],
            proposed_entry.get("text", unmatched_entry["text"]),
            proposed_entry,
        )
        return {
            "status": "value_added",
            "entry": proposed_entry,
            "collection": unmatched_entry["label"],
        }

    return {
        "status": "clarification_needed",
        "message": (
            f'Please clarify again: what does "{unmatched_entry["text"]}" '
            f'mean in the context of {unmatched_entry["label"]}?'
        ),
        "entry": unmatched_entry,
    }


# ── Stub (to be implemented) ────────────────────────────────────────

def add_embedding_to_db(collection_name, text, payload):
    """Add a new embedding to the specified collection in the vector database."""
    pass
