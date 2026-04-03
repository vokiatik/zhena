from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from sweater.schemas.process.attribute_schema import CreateProcessAttribute, UpdateProcessAttribute
from sweater.services.process.attributes_service import (
    get_table_columns,
    get_process_attributes_by_process_id,
    create_process_attribute_,
    update_process_attribute_,
    delete_process_attribute_,
)
from sweater.models.process_settings.Process_type_model import ProcessType
from sweater.database.references_db import get_reference_db
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles

router = APIRouter(prefix="/process/attributes", tags=["process_attributes"])

@router.get("/list")
def list_table_columns(
    table_name: str = "retail",
    type_id: str = None,
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_reference_db),
):
    # Resolve type_id to table_name if provided
    resolved_name = table_name
    if type_id:
        ptype = db.query(ProcessType).filter(ProcessType.id == type_id).first()
        if ptype and ptype.table_name:
            resolved_name = ptype.table_name
    columns = get_table_columns(resolved_name)
    return columns

@router.get("/{process_id}")
def get_process_attributes(process_id: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    attributes = get_process_attributes_by_process_id(db, process_id)
    return attributes

@router.post("/create")
def create_attribute(attribute: CreateProcessAttribute, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    new_attribute = create_process_attribute_(db, attribute)
    return new_attribute

@router.delete("/delete/{process_id}/{attribute_id}")
def delete_attribute(process_id: str, attribute_id: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    attribute = delete_process_attribute_(db, process_id, attribute_id)
    if attribute:
        return {"message": "Attribute deleted successfully"}
    else:
        return {"message": "Attribute not found"}

@router.put("/update/{process_id}")
def update_attribute(process_id: str, updated_attribute: UpdateProcessAttribute, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    attribute = update_process_attribute_(db, process_id, updated_attribute)
    if attribute:
        return attribute
    else:
        return {"message": "Attribute not found"}