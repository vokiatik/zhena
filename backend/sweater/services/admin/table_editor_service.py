from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from sweater.models.admin.table_admin_settings_model import TableAdminSettings


# ─── Table admin settings CRUD ────────────────────────────────────────────────

def list_table_settings(db: Session):
    return db.query(TableAdminSettings).order_by(TableAdminSettings.display_name).all()


def update_table_setting(db: Session, setting_id: str, visible: bool, only_admin: bool, editable: bool):
    setting = db.query(TableAdminSettings).filter(TableAdminSettings.id == setting_id).first()
    if not setting:
        return None
    setting.visible = visible
    setting.only_admin = only_admin
    setting.editable = editable
    db.commit()
    db.refresh(setting)
    return setting


def list_visible_tables(db: Session, is_admin: bool):
    """Return the tables visible to this user."""
    query = db.query(TableAdminSettings).filter(TableAdminSettings.visible == True)
    if not is_admin:
        query = query.filter(TableAdminSettings.only_admin == False)
    return query.order_by(TableAdminSettings.display_name).all()


# ─── Dynamic table editor ─────────────────────────────────────────────────────

def _allowed_table(db: Session, table_name: str) -> TableAdminSettings | None:
    """Return the setting row if the table is allowed to be accessed."""
    return db.query(TableAdminSettings).filter(
        TableAdminSettings.table_name == table_name,
        TableAdminSettings.visible == True,
    ).first()


def get_table_schema(db: Session, table_name: str) -> list[dict]:
    """Return column definitions for a reference table."""
    setting = _allowed_table(db, table_name)
    if not setting:
        return []

    inspector = inspect(db.bind)
    columns = inspector.get_columns(table_name)
    return [
        {
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col["nullable"],
            "primary_key": col["name"] in [
                pk for pk in inspector.get_pk_constraint(table_name).get("constrained_columns", [])
            ],
        }
        for col in columns
    ]


def get_table_rows(
    db: Session,
    table_name: str,
    page: int = 1,
    page_size: int = 20,
    sort_column: str | None = None,
    sort_dir: str = "asc",
) -> dict[str, Any]:
    """Return paginated rows from a reference table."""
    setting = _allowed_table(db, table_name)
    if not setting:
        return {"rows": [], "total": 0}

    # Validate sort_column against actual columns to prevent injection
    inspector = inspect(db.bind)
    valid_columns = {col["name"] for col in inspector.get_columns(table_name)}

    order_clause = ""
    if sort_column and sort_column in valid_columns:
        direction = "DESC" if sort_dir.lower() == "desc" else "ASC"
        order_clause = f'ORDER BY "{sort_column}" {direction}'

    offset = (page - 1) * page_size

    count_result = db.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
    total = count_result.scalar()

    rows_result = db.execute(
        text(f'SELECT * FROM "{table_name}" {order_clause} LIMIT :limit OFFSET :offset'),
        {"limit": page_size, "offset": offset},
    )
    rows = [dict(row._mapping) for row in rows_result]

    return {"rows": rows, "total": total}


def delete_table_row(db: Session, table_name: str, row_id: str) -> bool:
    """Delete a single row by its primary key (assumed 'id' column)."""
    setting = _allowed_table(db, table_name)
    if not setting or not setting.editable:
        return False

    db.execute(
        text(f'DELETE FROM "{table_name}" WHERE id = :row_id'),
        {"row_id": row_id},
    )
    db.commit()
    return True


def update_table_row(db: Session, table_name: str, row_id: str, data: dict[str, Any]) -> bool:
    """Update a single row by its primary key. Strips 'id' from data."""
    setting = _allowed_table(db, table_name)
    if not setting or not setting.editable:
        return False

    data.pop("id", None)
    if not data:
        return False

    # Validate columns against actual table schema to prevent injection
    inspector = inspect(db.bind)
    valid_columns = {col["name"] for col in inspector.get_columns(table_name)}
    safe_data = {k: v for k, v in data.items() if k in valid_columns}

    if not safe_data:
        return False

    set_clause = ", ".join(f'"{col}" = :{col}' for col in safe_data)
    safe_data["_row_id"] = row_id

    db.execute(
        text(f'UPDATE "{table_name}" SET {set_clause} WHERE id = :_row_id'),
        safe_data,
    )
    db.commit()
    return True
