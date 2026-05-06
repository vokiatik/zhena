from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles
from sweater.schemas.admin.table_editor_schema import TableSettingUpdate, RowUpdateRequest, RowCreateRequest
from sweater.services.admin.table_editor_service import (
    list_table_settings,
    update_table_setting,
    list_visible_tables,
    get_table_schema,
    get_table_rows,
    delete_table_row,
    update_table_row,
    create_table_row,
    get_fk_options,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ─── Table admin settings meta endpoints ──────────────────────────────────────

@router.get(
    "/table-settings",
    dependencies=[Depends(require_roles("admin"))],
)
def get_all_table_settings(db: Session = Depends(get_reference_db)):
    settings = list_table_settings(db)
    return {"success": True, "data": [
        {
            "id": str(s.id),
            "table_name": s.table_name,
            "display_name": s.display_name,
            "visible": s.visible,
            "only_admin": s.only_admin,
            "editable": s.editable,
        }
        for s in settings
    ]}


@router.put(
    "/table-settings/{setting_id}",
    dependencies=[Depends(require_roles("admin"))],
)
def update_table_settings(
    setting_id: str,
    body: TableSettingUpdate,
    db: Session = Depends(get_reference_db),
):
    result = update_table_setting(db, setting_id, body.visible, body.only_admin, body.editable)
    if not result:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {
        "success": True,
        "data": {
            "id": str(result.id),
            "table_name": result.table_name,
            "display_name": result.display_name,
            "visible": result.visible,
            "only_admin": result.only_admin,
            "editable": result.editable,
        },
    }


# ─── Dynamic table editor endpoints ───────────────────────────────────────────

@router.get(
    "/table-editor/tables",
    dependencies=[Depends(require_roles("admin"))],
)
def get_visible_tables(db: Session = Depends(get_reference_db)):
    tables = list_visible_tables(db, is_admin=True)
    return {"success": True, "data": [
        {
            "id": str(t.id),
            "table_name": t.table_name,
            "display_name": t.display_name,
            "editable": t.editable,
        }
        for t in tables
    ]}


@router.get(
    "/table-editor/fk-options/{ref_table}",
    dependencies=[Depends(require_roles("admin"))],
)
def get_fk_options_route(
    ref_table: str,
    label_column: str,
    db: Session = Depends(get_reference_db),
):
    options = get_fk_options(db, ref_table, label_column)
    return {"success": True, "data": options}


@router.get(
    "/table-editor/{table_name}/schema",
    dependencies=[Depends(require_roles("admin"))],
)
def get_schema(table_name: str, db: Session = Depends(get_reference_db)):
    schema = get_table_schema(db, table_name)
    if not schema:
        raise HTTPException(status_code=404, detail="Table not found or not accessible")
    return {"success": True, "data": schema}


@router.get(
    "/table-editor/{table_name}/rows",
    dependencies=[Depends(require_roles("admin"))],
)
def get_rows(
    table_name: str,
    page: int = 1,
    page_size: int = 20,
    sort_column: str | None = None,
    sort_dir: str = "asc",
    db: Session = Depends(get_reference_db),
):
    result = get_table_rows(db, table_name, page, page_size, sort_column, sort_dir)
    if result["total"] == 0 and page > 1:
        return {"success": True, "data": result}
    return {"success": True, "data": result}


@router.post(
    "/table-editor/{table_name}/rows",
    dependencies=[Depends(require_roles("admin"))],
)
def create_row(
    table_name: str,
    body: RowCreateRequest,
    db: Session = Depends(get_reference_db),
):
    row = create_table_row(db, table_name, body.data)
    if row is None:
        raise HTTPException(status_code=400, detail="Insert failed or table not editable")
    return {"success": True, "data": row}


@router.delete(
    "/table-editor/{table_name}/rows/{row_id}",
    dependencies=[Depends(require_roles("admin"))],
)
def delete_row(table_name: str, row_id: str, db: Session = Depends(get_reference_db)):
    ok = delete_table_row(db, table_name, row_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Row not found or table not editable")
    return {"success": True}


@router.put(
    "/table-editor/{table_name}/rows/{row_id}",
    dependencies=[Depends(require_roles("admin"))],
)
def update_row(
    table_name: str,
    row_id: str,
    body: RowUpdateRequest,
    db: Session = Depends(get_reference_db),
):
    ok = update_table_row(db, table_name, row_id, body.data)
    if not ok:
        raise HTTPException(status_code=400, detail="Update failed or table not editable")
    return {"success": True}
