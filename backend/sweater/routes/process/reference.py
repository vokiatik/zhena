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
from sweater.schemas.process.reference_schema import CreateReference, UpdateReference
from sweater.database.references_db import get_reference_db

router = APIRouter(prefix="/reference", tags=["process_attributes_reference"])

@router.get("/types_list")
def list_reference_types(db: Session = Depends(get_reference_db)):
    reference_types_list = list_reference_types_(db)
    return reference_types_list

@router.get("/{reference_type_id}")
def get_references_by_type(reference_type_id: str, db: Session = Depends(get_reference_db)):
    ref_list = get_references_by_type_(db, reference_type_id)
    return {"success": True, "data": ref_list}

@router.post("/create_type")
def create_reference_type(r: CreateReference, db: Session = Depends(get_reference_db)):
    result = create_reference_type_(db, r.value)
    return {"success": True, "data": result}

@router.delete("/delete_type/{reference_type_id}")
def delete_reference_type(reference_type_id: str, db: Session = Depends(get_reference_db)):
    result = delete_reference_type_(db, reference_type_id)
    return {"success": True, "data": result}

@router.post("/add_value/{reference_type_id}")
def add_value_to_reference(reference_type_id: str, r: CreateReference, db: Session = Depends(get_reference_db)):
    result = add_value_to_reference_(db, reference_type_id, r.value)
    return {"success": True, "data": result}

@router.delete("/delete_value/{reference_id}")
def delete_value_from_reference(reference_id: str, db: Session = Depends(get_reference_db)):
    result = delete_value_from_reference_(db, reference_id)
    return {"success": True, "data": result}

@router.put("/update_value/{reference_id}")
def update_value_of_reference(r: UpdateReference, db: Session = Depends(get_reference_db)):
    result = update_value_of_reference_(db, r.id, r.value)
    return {"success": True, "data": result}