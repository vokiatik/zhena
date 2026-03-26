from fastapi import APIRouter
from fastapi.params import Depends
from requests import Session
from sweater.services.process.reference_service import list_reference_types_, get_references_by_type_, create_reference_type_, delete_reference_type_, add_value_to_reference_, update_value_of_reference_,delete_value_from_reference_
from sweater.database.base_db import get_db
from sweater.database.references_db import get_reference_db

router = APIRouter(prefix="/process/attributes/reference", tags=["process_attributes_reference"])

@router.get("/types_list")
def list_reference_types(db: Session = Depends(get_reference_db)):
    reference_types = list_reference_types_(db)
    return reference_types

@router.get("/{reference_type_id}")
def get_references_by_type(reference_type_id: str, db: Session = Depends(get_reference_db)):
    references = get_references_by_type_(db, reference_type_id)
    return references

@router.post("/create_type")
def create_reference_type(reference_type: str, db: Session = Depends(get_reference_db)):
    new_reference_type = create_reference_type_(db, reference_type)
    return new_reference_type

@router.delete("/delete_type/{reference_type_id}")
def delete_reference_type(reference_type_id: str, db: Session = Depends(get_reference_db)):
    result = delete_reference_type_(db, reference_type_id)
    return result

    
@router.get("/add_value/{reference_id}")
def add_value_to_reference(reference_id: str, value: str, db: Session = Depends(get_reference_db)):
    reference = add_value_to_reference_(db, reference_id, value)
    return reference
    
@router.delete("/delete_value/{reference_id}")
def delete_value_from_reference(reference_id: str, db: Session = Depends(get_reference_db)):
    reference = delete_value_from_reference_(db, reference_id)
    return reference
    
@router.put("/update_value/{reference_id}")
def update_value_of_reference(reference_id: str, new_value: str, db: Session = Depends(get_reference_db)):
    reference = update_value_of_reference_(db, reference_id, new_value)
    return reference
    

    