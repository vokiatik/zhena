from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from sweater.models.admin.table_admin_settings_model import TableAdminSettings

# ── Import every Reference_Base model so Reference_Base.metadata knows about
# all tables.  Required for Python-default introspection.
from sweater.models.process_settings.Picture_attribute_reference_model import PictureAttributeReference  # noqa: F401
from sweater.models.process_settings.Picture_attribute_reference_type_model import PictureAttributeReferenceType  # noqa: F401
from sweater.models.process_settings.Picture_processing_model import ProcessSettings as _ProcessSettings  # noqa: F401
from sweater.models.process_settings.Process_model import Process as _Process  # noqa: F401
from sweater.models.process_settings.Process_attributes_crosstable_model import ProcessAttributes as _ProcessAttributes  # noqa: F401
from sweater.models.process_settings.Process_type_model import ProcessType as _ProcessType  # noqa: F401
from sweater.models.process_settings.Process_status_model import ProcessStatus as _ProcessStatus  # noqa: F401
from sweater.models.Dictionaries.ecom_formats import EcomFormat as _EcomFormat  # noqa: F401
from sweater.models.retail.Retail_model import Retail as _Retail  # noqa: F401
from sweater.models.retail.Retail_model_additional import RetailAdditional as _RetailAdditional  # noqa: F401
from sweater.models.retail.Analyst_processed_model import AnalystProcessed as _AnalystProcessed  # noqa: F401
from sweater.models.retail.Retail_processed_model import RetailProcessed as _RetailProcessed  # noqa: F401


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


# ─── Constants ────────────────────────────────────────────────────────────────

# Column names that are always auto-managed by the DB.
# These are hidden from the Add-Row form and never accepted from the caller.
_AUTO_FIELD_NAMES = frozenset({
    "created_at", "updated_at", "deleted_at",
    "deleted", "is_deleted",
})

# Explicit FK relationships (models don't use ForeignKey() declarations).
# Format: {table_name: {col_name: (referenced_table, label_column)}}
FK_CONFIG: dict[str, dict[str, tuple[str, str]]] = {
    "picture_attribute_reference": {
        "reference_type_id": ("picture_attribute_reference_type", "reference_type_name"),
    },
    "process_settings": {
        "type": ("process_types", "process_type_name"),
    },
    "processes": {
        "type_id": ("process_types", "process_type_name"),
        "status_id": ("process_statuses", "process_status_name"),
    },
    "process_attributes": {
        "reference_type_id": ("picture_attribute_reference_type", "reference_type_name"),
        "process_id": ("process_settings", "title"),
    },
}


# ─── ORM helpers ──────────────────────────────────────────────────────────────

def _python_scalar_defaults(table_name: str) -> dict[str, Any]:
    """Return {col_name: default_value} for columns with scalar Python-level defaults.

    Only covers defaults declared as default=<scalar> in the ORM Column definition
    (not server_default, not callable defaults like uuid.uuid4).
    Uses Reference_Base.metadata which has every imported model registered.
    """
    from sweater.database.references_db import Reference_Base

    table_obj = Reference_Base.metadata.tables.get(table_name)
    if table_obj is None:
        return {}

    result: dict[str, Any] = {}
    for col in table_obj.columns:
        if (
            col.default is not None
            and hasattr(col.default, "arg")
            and not callable(col.default.arg)
            and col.server_default is None
        ):
            result[col.name] = col.default.arg
    return result


def _resolve_python_defaults(table_name: str) -> dict[str, Any]:
    """Return {col_name: value} for ALL Python-level Column defaults — both scalar
    and callable (e.g. uuid.uuid4).

    SQLAlchemy wraps callable defaults as ``lambda ctx: original_fn()`` so they
    must be called with a dummy context (None) rather than with no arguments.
    server_default columns are excluded — the DB handles those.
    """
    from sweater.database.references_db import Reference_Base

    table_obj = Reference_Base.metadata.tables.get(table_name)
    if table_obj is None:
        return {}

    result: dict[str, Any] = {}
    for col in table_obj.columns:
        d = col.default
        if d is None or col.server_default is not None:
            continue
        if getattr(d, "is_scalar", False):
            result[col.name] = d.arg
        elif getattr(d, "is_callable", False):
            # SA wraps the original callable as `lambda ctx: original()`.
            # Pass None as a dummy context — the wrapper ignores it for
            # zero-argument originals like uuid.uuid4.
            try:
                result[col.name] = d.arg(None)
            except Exception:
                pass  # context-dependent default; skip
    return result


def get_table_schema(db: Session, table_name: str) -> list[dict]:
    """Return column definitions for a table in the reference database.

    Each column includes:
    - auto_generated: True → skip in Add form (PK, server default, or auto-name).
    - default_value:  scalar Python default to pre-fill in the form (or None).
    - foreign_key:    {table, label_column} if the column references another table.
    """
    setting = _allowed_table(db, table_name)
    if not setting:
        return []

    inspector = inspect(db.bind)
    columns = inspector.get_columns(table_name)
    pk_cols = set(inspector.get_pk_constraint(table_name).get("constrained_columns", []))

    python_defaults = _python_scalar_defaults(table_name)
    table_fk_cfg = FK_CONFIG.get(table_name, {})

    result = []
    for col in columns:
        col_name = col["name"]
        has_server_default = col.get("default") is not None
        is_pk = col_name in pk_cols
        auto_generated = (
            is_pk
            or has_server_default
            or bool(col.get("autoincrement"))
            or col_name in _AUTO_FIELD_NAMES
        )

        fk_info = None
        if col_name in table_fk_cfg:
            ref_table, ref_label = table_fk_cfg[col_name]
            fk_info = {"table": ref_table, "label_column": ref_label}

        result.append({
            "name": col_name,
            "type": str(col["type"]),
            "nullable": col["nullable"],
            "primary_key": is_pk,
            "auto_generated": auto_generated,
            # Scalar Python default to pre-fill; None for auto-generated cols or no default
            "default_value": python_defaults.get(col_name),
            "foreign_key": fk_info,
        })

    return result


def get_fk_options(db: Session, ref_table: str, label_column: str) -> list[dict]:
    """Return [{value, label}] for every row in a referenced table."""
    inspector = inspect(db.bind)
    if ref_table not in inspector.get_table_names():
        return []
    valid_cols = {c["name"] for c in inspector.get_columns(ref_table)}
    if label_column not in valid_cols:
        return []

    rows = db.execute(
        text(f'SELECT id, "{label_column}" FROM "{ref_table}" ORDER BY "{label_column}"')
    )
    return [
        {
            "value": str(row.id),
            "label": str(row[label_column]) if row[label_column] is not None else "(empty)",
        }
        for row in rows
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


def create_table_row(db: Session, table_name: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Insert a new row.

    Auto-managed columns (PKs, server-default cols, _AUTO_FIELD_NAMES) are never
    sourced from the caller.  For auto-cols that only have a Python-level default
    (e.g. deleted=False — NOT NULL but no DB default), we inject that default
    so the INSERT doesn't fail.
    """
    setting = _allowed_table(db, table_name)
    if not setting or not setting.editable:
        return None

    inspector = inspect(db.bind)
    columns = inspector.get_columns(table_name)
    pk_cols = set(inspector.get_pk_constraint(table_name).get("constrained_columns", []))

    auto_cols: set[str] = set(pk_cols) | _AUTO_FIELD_NAMES
    for col in columns:
        if col.get("default") is not None or bool(col.get("autoincrement")):
            auto_cols.add(col["name"])

    valid_columns = {col["name"] for col in columns}

    # User-provided values, stripped of auto columns
    safe_user_data = {
        k: v for k, v in data.items()
        if k in valid_columns and k not in auto_cols
    }

    # Inject Python defaults for all auto-cols that have one (scalar or callable).
    # This covers: id=uuid4(), deleted=False, is_shown=True, etc.
    # server_default columns (created_at) are excluded — the DB handles those.
    python_defaults = _resolve_python_defaults(table_name)
    auto_python_defaults = {
        col_name: python_defaults[col_name]
        for col_name in auto_cols
        if col_name in python_defaults
    }

    final_data = {**auto_python_defaults, **safe_user_data}

    if final_data:
        cols_clause = ", ".join(f'"{col}"' for col in final_data)
        vals_clause = ", ".join(f':{col}' for col in final_data)
        stmt = text(f'INSERT INTO "{table_name}" ({cols_clause}) VALUES ({vals_clause}) RETURNING *')
    else:
        stmt = text(f'INSERT INTO "{table_name}" DEFAULT VALUES RETURNING *')

    result = db.execute(stmt, final_data)
    db.commit()
    row = result.fetchone()
    return dict(row._mapping) if row else None


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
