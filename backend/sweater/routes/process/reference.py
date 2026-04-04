from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from sweater.services.process.reference_service import (
    list_reference_types_,
    get_references_by_type_,
    create_reference_type_,
    delete_reference_type_,
    add_value_to_reference_,
    update_value_of_reference_,
    delete_value_from_reference_,
)
from sweater.database.references_db import get_reference_db
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles

router = APIRouter(prefix="/reference", tags=["process_attributes_reference"])

@router.get("/types_list")
def list_reference_types(user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    reference_types_list = list_reference_types_(db)
    return {"success": True, "data": reference_types_list}

@router.get("/{reference_type_id}")
def get_references_by_type(reference_type_id: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    ref_list = get_references_by_type_(db, reference_type_id)
    return {"success": True, "data": ref_list}

@router.post("/create_type")
def create_reference_type(reference_type: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    result = create_reference_type_(db, reference_type)
    return {"success": True, "data": result}

@router.delete("/delete_type/{reference_type_id}")
def delete_reference_type(reference_type_id: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    result = delete_reference_type_(db, reference_type_id)
    return {"success": True, "data": result}

@router.post("/add_value/{reference_type_id}")
def add_value_to_reference(reference_type_id: str, value: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    result = add_value_to_reference_(db, reference_type_id, value)
    return {"success": True, "data": result}

@router.delete("/delete_value/{reference_id}")
def delete_value_from_reference(reference_id: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    result = delete_value_from_reference_(db, reference_id)
    return {"success": True, "data": result}

@router.put("/update_value/{reference_id}")
def update_value_of_reference(reference_id: str, new_value: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    result = update_value_of_reference_(db, reference_id, new_value)
    return {"success": True, "data": result}