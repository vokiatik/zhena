import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sweater.database import get_pool
from sweater.auth import get_current_user

router = APIRouter(prefix="/pictures", tags=["pictures"])

ALLOWED_TABLES = {"pictures_set_a", "pictures_set_b"}


# ── Schemas ──────────────────────────────────────────────────────────

class VerifyRequest(BaseModel):
    id: str
    url: str
    table: str
    # Accept arbitrary extra fields that the user may have edited
    extra: dict[str, str] = {}


# ── Routes ───────────────────────────────────────────────────────────

@router.get("/{table_name}")
async def get_unverified_pictures(table_name: str, user: dict = Depends(get_current_user)):
    """Return all rows from *table_name* where verified = FALSE."""
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail="Invalid table name")

    pool = await get_pool()
    rows = await pool.fetch(
        f"SELECT * FROM {table_name} WHERE verified = FALSE ORDER BY created_at"
    )

    results = []
    for r in rows:
        item: dict = {k: (str(v) if isinstance(v, uuid.UUID) else v) for k, v in dict(r).items()}
        results.append(item)
    return results


@router.post("/{table_name}/verify")
async def verify_picture(table_name: str, body: VerifyRequest, user: dict = Depends(get_current_user)):
    """Update a row with any extra fields provided, then mark it as verified."""
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail="Invalid table name")
    if body.table != table_name:
        raise HTTPException(status_code=400, detail="Table name mismatch")

    pool = await get_pool()
    row_id = uuid.UUID(body.id)

    # Build dynamic SET clause for extra fields
    set_parts = ["verified = TRUE"]
    values: list = [row_id, body.url]
    idx = 3  # $1 = id, $2 = url, $3+ = extra fields

    # Fetch current column names to only allow real columns
    columns = await pool.fetch(
        "SELECT column_name FROM information_schema.columns WHERE table_name = $1",
        table_name,
    )
    valid_columns = {r["column_name"] for r in columns} - {"id", "verified", "created_at"}

    for col, val in body.extra.items():
        if col not in valid_columns:
            continue
        set_parts.append(f"{col} = ${idx}")
        values.append(val)
        idx += 1

    query = f"UPDATE {table_name} SET {', '.join(set_parts)} WHERE id = $1 AND url = $2"
    result = await pool.execute(query, *values)

    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Picture not found")

    return {"ok": True}
