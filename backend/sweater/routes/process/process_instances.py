"""
Process-instances HTTP endpoints.

Workflow for the monthly report (data_prep process type):
  1. POST /{process_id}/upload-file       – upload + validate file
  1b. POST /{process_id}/confirm-dict     – resolve missing dict values + save
  2. POST /{process_id}/provide-link      – store cloud link (placeholder)
  3. POST /{process_id}/analyst-confirm   – analyst finishes review
  4. POST /{process_id}/marketing-confirm – marketing confirms, mark completed
"""

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles
from sweater.schemas.process.process_instance_schema import (
    CreateDataPrepProcess,
    ProvideLinkBody,
    UpdateProcessInstance,
)
from sweater.models.process_settings.Process_status_model import ProcessStatus
from sweater.services.process.process_instance_service import (
    list_process_instances,
    create_process_instance,
    update_process_status,
    get_process_instance_by_id,
    get_process_type_name,
    get_process_status_name,
)
from sweater.services.upload.advertisement_parsing_service import (
    parse_advertisement_file,
    save_advertisement_dataframe_to_db,
    parse_links_placeholder,
)
from sweater.services.upload.advertisement_validation_service import (
    check_all_missing,
    apply_simple_value_decisions,
    save_new_simple_values,
    save_new_format,
    save_new_detector_mapping,
)

router = APIRouter(prefix="/process-instances", tags=["process_instances"])


# ── Status list ──────────────────────────────────────────────────

@router.get("/statuses")
async def get_process_statuses(
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    statuses = db.query(ProcessStatus).all()
    return [s.process_status_name for s in statuses]


# ── Process list ─────────────────────────────────────────────────

@router.get("/list")
async def get_process_list(
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    return list_process_instances(db)


# ── Single process ───────────────────────────────────────────────

@router.get("/{process_id}")
async def get_process(
    process_id: str,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    return {
        "id": str(process.id),
        "type_name": get_process_type_name(db, process),
        "status_name": get_process_status_name(db, process),
        "comment": process.comment,
        "initiator_id": str(process.initiator_id) if process.initiator_id else None,
        "total_items": process.total_items,
        "parent_process_id": str(process.parent_process_id) if process.parent_process_id else None,
        "created_at": process.created_at.isoformat() if process.created_at else None,
    }


# ── Create data_prep process ─────────────────────────────────────

@router.post("/create")
async def create_data_prep_process(
    body: CreateDataPrepProcess,
    user: dict = Depends(require_roles("admin", "analyst")),
    db: Session = Depends(get_reference_db),
):
    process = create_process_instance(
        db,
        type_name="data_prep",
        comment=body.comment,
        initiator_id=user["id"],
    )
    return {"ok": True, "process_id": str(process.id)}


# ── Step 1 – File upload ─────────────────────────────────────────

@router.post("/{process_id}/upload-file")
async def upload_file_for_process(
    process_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(require_roles("admin", "analyst")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    if get_process_status_name(db, process) != "initiated":
        raise HTTPException(status_code=400, detail="Process is not in the 'initiated' state")

    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is missing.")
    lower = file.filename.lower()
    if not (lower.endswith(".csv") or lower.endswith(".xlsx") or lower.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only CSV, XLSX and XLS are allowed.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        df = parse_advertisement_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    missing_values, existing_by_field = check_all_missing(db, df)
    if missing_values:
        return {
            "status": "needs_validation",
            "missing_values": missing_values,
            "existing_values_by_field": existing_by_field,
        }

    # All values found – save and advance
    process.comment = file.filename
    db.commit()
    inserted = save_advertisement_dataframe_to_db(db, df, process_id=process.id)
    process.total_items = inserted
    db.commit()
    update_process_status(db, process_id, "awaiting_link")

    return {"ok": True, "inserted": inserted}


# ── Step 1b – Confirm dict decisions + re-upload ─────────────────

@router.post("/{process_id}/confirm-dict")
async def confirm_dict_for_process(
    process_id: str,
    file: UploadFile = File(...),
    decisions: str = Form(...),
    user: dict = Depends(require_roles("admin", "analyst")),
    db: Session = Depends(get_reference_db),
):
    """
    Accepts the file again together with user decisions for each missing value.

    Each decision object:
      {
        "field":            "brand",        # field_name
        "original_value":   "SomeBrand",    # the raw cell value
        "save":             true,           # add to dictionary
        "replace_with":     null,           # or a replacement value (when save=false)

        # For format decisions only:
        "new_format_value":   "NewFormat",  # user wants to add new format row
        "link_to_format_id":  "uuid",       # or link to existing format
      }
    """
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    if get_process_status_name(db, process) != "initiated":
        raise HTTPException(status_code=400, detail="Process is not in the 'initiated' state")

    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is missing.")
    lower = file.filename.lower()
    if not (lower.endswith(".csv") or lower.endswith(".xlsx") or lower.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only CSV, XLSX and XLS are allowed.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        raw_decisions = json.loads(decisions)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid decisions payload.")

    try:
        df = parse_advertisement_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Persist new simple values and apply replacements
    simple_decisions = [d for d in raw_decisions if d.get("field") != "format"]
    save_new_simple_values(db, simple_decisions)
    df = apply_simple_value_decisions(df, simple_decisions)

    # Persist new / mapped formats
    for d in raw_decisions:
        if d.get("field") != "format":
            continue
        orig = d.get("original_value", "").strip()
        if d.get("new_format_value"):
            save_new_format(db, d["new_format_value"], detector_value=orig)
        elif d.get("link_to_format_id"):
            save_new_detector_mapping(db, orig, d["link_to_format_id"])

    process.comment = file.filename
    db.commit()
    inserted = save_advertisement_dataframe_to_db(db, df, process_id=process.id)
    process.total_items = inserted
    db.commit()
    update_process_status(db, process_id, "awaiting_link")

    return {"ok": True, "inserted": inserted}


# ── Step 2 – Provide link ────────────────────────────────────────

@router.post("/{process_id}/provide-link")
async def provide_link_for_process(
    process_id: str,
    body: ProvideLinkBody,
    user: dict = Depends(require_roles("admin", "analyst")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    if get_process_status_name(db, process) != "awaiting_link":
        raise HTTPException(status_code=400, detail="Process is not in the 'awaiting_link' state")

    if not body.link.strip():
        raise HTTPException(status_code=400, detail="Link cannot be empty.")

    # Store link; blank picture-loading function (to be implemented later)
    process.comment = body.link.strip()
    db.commit()
    _load_pictures_from_link_placeholder(body.link.strip())
    update_process_status(db, process_id, "analyst_review")

    return {"ok": True}


def _load_pictures_from_link_placeholder(link: str) -> None:
    """Placeholder: load pictures from cloud link into the DB. To be implemented."""
    pass


# ── Step 3 – Analyst confirms review ────────────────────────────

@router.post("/{process_id}/analyst-confirm")
async def analyst_confirm(
    process_id: str,
    user: dict = Depends(require_roles("admin", "analyst")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    if get_process_status_name(db, process) != "analyst_review":
        raise HTTPException(status_code=400, detail="Process is not in the 'analyst_review' state")

    update_process_status(db, process_id, "marketing_review")
    return {"ok": True}


# ── Step 4 – Marketing analyst confirms review ───────────────────

@router.post("/{process_id}/marketing-confirm")
async def marketing_confirm(
    process_id: str,
    user: dict = Depends(require_roles("admin", "marketing_specialist")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    if get_process_status_name(db, process) != "marketing_review":
        raise HTTPException(status_code=400, detail="Process is not in the 'marketing_review' state")

    _upload_to_clickhouse_placeholder(process_id)
    update_process_status(db, process_id, "completed")
    return {"ok": True}


def _upload_to_clickhouse_placeholder(process_id: str) -> None:
    """Placeholder: upload final data to ClickHouse. To be implemented."""
    pass


# ── Cancel process ───────────────────────────────────────────────

@router.post("/{process_id}/cancel")
async def cancel_process(
    process_id: str,
    user: dict = Depends(require_roles("admin", "analyst")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    current_status = get_process_status_name(db, process)
    if current_status in ("completed", "canceled"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a process with status '{current_status}'")

    update_process_status(db, process_id, "canceled")
    return {"ok": True}


# ── Admin: manual status update ──────────────────────────────────

@router.put("/update/{process_id}")
async def update_process(
    process_id: str,
    body: UpdateProcessInstance,
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    if body.status:
        updated = update_process_status(db, process_id, body.status)
        if not updated:
            raise HTTPException(status_code=400, detail="Invalid status")

    if body.comment is not None:
        process.comment = body.comment
        db.commit()

    return {"ok": True}

