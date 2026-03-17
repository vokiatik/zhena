import requests

from sweater.query_analisys_tools.config import OLLAMA_URL, OLLAMA_MODEL

DUCKLING_URL = "http://localhost:8000/parse"


def _normalize_date_expression(text):
    """Use a local LLM to rewrite ambiguous date expressions into forms Duckling understands."""
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "user", "content": (
                f"You are a helpful assistant that rewrites user-provided date expressions into explicit English date ranges."
                f"Rewrite \"{text}\" as an English date range. Avoid any abbreviations and slang. Make it as explicit as possible. "
                "Reply with ONLY the date range, no explanation. "
            )}
        ],
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_predict": 50}
    })
    data = response.json()
    return data["message"]["content"].strip()


def _duckling_parse(text):
    """Send text to Duckling and return parsed result."""
    data = {
        "text": text,
        "locale": "en_US",
        "dims": "[\"time\"]"
    }
    r = requests.post(DUCKLING_URL, data=data)
    return r.json()


def parse_date_range(text):
    """Parse a date expression into structured date range via Duckling, with LLM fallback."""
    result = _duckling_parse(text)
    if result:
        return result

    normalized = _normalize_date_expression(text)
    result = _duckling_parse(normalized)
    return result


def date_sql_filter(column, start, end):
    return f"{column} BETWEEN '{start[:10]}' AND '{end[:10]}'"