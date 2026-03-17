import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query

from sweater.database import get_pool
from sweater.query_analisys_tools.pipeline import (
    extract_and_match,
    compare_metrics,
    build_sql_query,
)
from sweater.query_analisys_tools.query_decomposer import decompose_query
from sweater.query_analisys_tools.clarification import (
    handle_clarification,
    handle_new_value_confirmation,
    build_clarification_message,
)
from sweater.auth import get_current_user, decode_jwt

# Per-connection state for pending clarifications: chat_id -> list of unmatched entries
_pending_clarifications: dict[str, dict] = {}

# Human-readable labels for each processing status
STATUS_LABELS = {
    "analyzing": "Analyzing your message…",
    "extracting_entities": "Extracting entities from query…",
    "searching_database": "Searching database for matches…",
    "checking_data": "Checking for unknown data…",
    "building_query": "Building SQL query…",
    "complete": "Complete",
}

router = APIRouter()


# ── REST endpoints for chat history ──────────────────────────────────

@router.get("/chats")
async def list_chats(user: dict = Depends(get_current_user)):
    """Return all chats for the authenticated user ordered by most recent first."""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT id, title, created_at FROM chats WHERE user_id = $1 ORDER BY created_at DESC",
        uuid.UUID(user["id"]),
    )
    return [
        {"id": str(r["id"]), "title": r["title"], "createdAt": r["created_at"].isoformat()}
        for r in rows
    ]


@router.get("/chats/{chat_id}/messages")
async def get_messages(chat_id: uuid.UUID, user: dict = Depends(get_current_user)):
    """Return all messages for a chat owned by the authenticated user."""
    pool = await get_pool()
    # Verify ownership
    owner = await pool.fetchval(
        "SELECT user_id FROM chats WHERE id = $1", chat_id,
    )
    if owner is None or str(owner) != user["id"]:
        raise HTTPException(status_code=404, detail="Chat not found")

    rows = await pool.fetch(
        "SELECT id, role, content, created_at FROM messages WHERE chat_id = $1 ORDER BY created_at",
        chat_id,
    )
    return [
        {
            "id": str(r["id"]),
            "role": r["role"],
            "content": r["content"],
            "timestamp": int(r["created_at"].timestamp() * 1000),
        }
        for r in rows
    ]


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: uuid.UUID, user: dict = Depends(get_current_user)):
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM chats WHERE id = $1 AND user_id = $2",
        chat_id, uuid.UUID(user["id"]),
    )
    return {"ok": True}


# ── WebSocket ────────────────────────────────────────────────────────

@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket, token: str = Query(...)):
    # Authenticate via token query parameter
    try:
        payload = decode_jwt(token)
        user_id = payload["sub"]
    except Exception:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            msg_type = data.get("type")

            if msg_type == "new_chat":
                chat_id, title = await _create_chat(user_id, data.get("title", "New Chat"))
                await websocket.send_text(json.dumps({
                    "type": "chat_created",
                    "chatId": chat_id,
                    "title": title,
                }))

            elif msg_type == "message":
                chat_id = data.get("chatId")
                content = data.get("content", "").strip()
                if not chat_id or not content:
                    continue

                pool = await get_pool()
                owner = await pool.fetchval(
                    "SELECT user_id FROM chats WHERE id = $1", uuid.UUID(chat_id),
                )
                if owner is None or str(owner) != user_id:
                    continue

                user_msg = await _save_message(chat_id, "user", content)
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "chatId": chat_id,
                    "message": user_msg,
                }))

                pending = _pending_clarifications.get(chat_id)

                if pending and pending.get("state") == "awaiting_clarification":
                    # User is responding to a clarification request
                    answer_text = await _handle_clarification_flow(
                        chat_id, content, pending, websocket
                    )
                elif pending and pending.get("state") == "awaiting_confirmation":
                    # User is confirming a proposed new value (yes/no)
                    confirmed = content.lower() in ("yes", "y", "да")
                    entry = pending["current_entry"]
                    proposed = pending["proposed_entry"]
                    result = await asyncio.to_thread(
                        handle_new_value_confirmation, confirmed, proposed, entry
                    )
                    if result["status"] == "clarification_needed":
                        pending["state"] = "awaiting_clarification"
                        answer_text = result["message"]
                    else:
                        answer_text = await _advance_clarification(chat_id, pending)
                else:
                    # Fresh query — run the full pipeline with status updates
                    answer_text = await _run_pipeline_with_status(
                        chat_id, user_msg["id"], content, websocket
                    )

                assistant_msg = await _save_message(chat_id, "assistant", answer_text)
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "chatId": chat_id,
                    "message": assistant_msg,
                }))

            elif msg_type == "delete_chat":
                chat_id = data.get("chatId")
                if chat_id:
                    pool = await get_pool()
                    await pool.execute(
                        "DELETE FROM chats WHERE id = $1 AND user_id = $2",
                        uuid.UUID(chat_id), uuid.UUID(user_id),
                    )
                    await websocket.send_text(json.dumps({
                        "type": "chat_deleted",
                        "chatId": chat_id,
                    }))

    except WebSocketDisconnect:
        pass


# ── Clarification flow helpers ───────────────────────────────────────

async def _handle_clarification_flow(chat_id, user_response, pending, websocket):
    """Handle a user reply to a clarification prompt."""
    entry = pending["current_entry"]
    result = await asyncio.to_thread(handle_clarification, user_response, entry)

    if result["status"] == "confirm_new_value":
        pending["state"] = "awaiting_confirmation"
        pending["proposed_entry"] = result["proposed_entry"]
        return result["message"]

    # synonym_added — move to next unmatched or finish
    pending["matched"].append({
        "text": result["confirmed_value"],
        "label": entry["label"],
    })
    return await _advance_clarification(chat_id, pending)


async def _advance_clarification(chat_id, pending):
    """Move to the next unmatched entry or finalize if all are resolved."""
    idx = pending["current_index"] + 1
    unmatched = pending["unmatched"]

    if idx < len(unmatched):
        pending["current_index"] = idx
        pending["current_entry"] = unmatched[idx]
        pending["state"] = "awaiting_clarification"
        return (
            f'Please clarify: "{unmatched[idx]["text"]}" '
            f'(category: {unmatched[idx]["label"]})'
        )

    # All clarifications resolved — build final result
    from sweater.query_analisys_tools.pipeline import build_sql_query
    result = build_sql_query(pending["matched"], pending["decomposed"])
    _pending_clarifications.pop(chat_id, None)
    return json.dumps(result, indent=2)


# ── Helpers ──────────────────────────────────────────────────────────

async def _send_status(websocket: WebSocket, chat_id: str, message_id: str, status: str):
    """Save a processing status to the DB and push it to the client."""
    label = STATUS_LABELS.get(status, status)
    await _save_status(message_id, status, label)
    await websocket.send_text(json.dumps({
        "type": "status",
        "chatId": chat_id,
        "messageId": message_id,
        "status": status,
        "label": label,
    }))


async def _save_status(message_id: str, status: str, label: str):
    """Persist a processing status row."""
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO processing_statuses (message_id, status, label) VALUES ($1, $2, $3)",
        uuid.UUID(message_id), status, label,
    )


async def _run_pipeline_with_status(chat_id: str, message_id: str, content: str, websocket: WebSocket) -> str:
    """Run the query pipeline step-by-step, emitting status updates at each stage."""

    # Step 1 — Analyzing
    await _send_status(websocket, chat_id, message_id, "analyzing")

    # Step 2 — Extract entities + search DB (and decompose in parallel)
    await _send_status(websocket, chat_id, message_id, "extracting_entities")
    extraction_task = asyncio.to_thread(extract_and_match, content)
    decompose_task = asyncio.to_thread(decompose_query, content)
    (matched, unmatched), decomposed = await asyncio.gather(extraction_task, decompose_task)

    # Step 3 — Searching database (already done above, but the label is meaningful)
    await _send_status(websocket, chat_id, message_id, "searching_database")

    # Step 4 — Check for unknown data
    await _send_status(websocket, chat_id, message_id, "checking_data")
    metrics_match = compare_metrics(matched, decomposed)

    if not unmatched:
        # Step 5 — Build SQL
        await _send_status(websocket, chat_id, message_id, "building_query")
        result = build_sql_query(matched, decomposed)
        await _send_status(websocket, chat_id, message_id, "complete")
        _pending_clarifications.pop(chat_id, None)
        return json.dumps(result, indent=2)

    # Some entities are unmatched — ask for clarification
    await _send_status(websocket, chat_id, message_id, "complete")
    _pending_clarifications[chat_id] = {
        "state": "awaiting_clarification",
        "unmatched": list(unmatched),
        "matched": list(matched),
        "decomposed": decomposed,
        "current_index": 0,
        "current_entry": unmatched[0],
    }
    return build_clarification_message(unmatched)


async def _create_chat(user_id: str, title: str) -> tuple[str, str]:
    pool = await get_pool()
    row = await pool.fetchrow(
        "INSERT INTO chats (user_id, title) VALUES ($1, $2) RETURNING id, title",
        uuid.UUID(user_id), title[:255],
    )
    return str(row["id"]), row["title"]


async def _save_message(chat_id: str, role: str, content: str) -> dict:
    pool = await get_pool()
    row = await pool.fetchrow(
        "INSERT INTO messages (chat_id, role, content) VALUES ($1, $2, $3) "
        "RETURNING id, role, content, created_at",
        uuid.UUID(chat_id),
        role,
        content,
    )
    return {
        "id": str(row["id"]),
        "role": row["role"],
        "content": row["content"],
        "timestamp": int(row["created_at"].replace(tzinfo=timezone.utc).timestamp() * 1000),
    }
