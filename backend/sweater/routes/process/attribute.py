from fastapi import APIRouter
from fastapi.params import Depends
from requests import Session
from sweater.schemas.process.attribute_schema import Attribute, ProcessAttribute, ProcessAttributeReference
from sweater.services.process.attributes_service import get_process_attributes_by_process_id, create_process_attribute, update_process_attribute, delete_process_attribute, create_process_attribute_reference_cross, update_process_attribute_reference_cross

from sweater.database.base_db import get_db
from sweater.database.references_db import get_reference_db

from sweater.models.retail.Retail_model import Retail

router = APIRouter(prefix="/process/attributes", tags=["process_attributes"])

@router.get("/list")
def list_process_attributes(db: Session = Depends(get_reference_db)):
    attributes = Retail.model_fields
    attributes_list = [name for name, _ in attributes.items()] 
    return attributes_list

@router.get("/{process_id}")
def get_process_attributes(process_id: str, db: Session = Depends(get_reference_db)):
    attributes = get_process_attributes_by_process_id(db, process_id)
    return attributes

@router.post("/create")
def create_process_attribute(process_id: str, attribute: ProcessAttribute, db: Session = Depends(get_reference_db)):
    attribute = create_process_attribute(db, process_id, attribute)
    return attribute

@router.delete("/delete/{process_id}/{attribute_id}")
def delete_process_attribute(process_id: str, attribute_id: str, db: Session = Depends(get_reference_db)):
    attribute = delete_process_attribute(db, process_id, attribute_id)
    if attribute:
        return {"message": "Attribute deleted successfully"}
    else:
        return {"message": "Attribute not found"}
    
@router.put("/update/{process_id}")
def update_process_attribute(process_id: str, updated_attribute: Attribute, db: Session = Depends(get_reference_db)):
    attribute = update_process_attribute(db, process_id, updated_attribute)
    if attribute:
        return attribute
    else:
        return {"message": "Attribute not found"}


@router.post("/create_attribute_reference")
def create_reference_value(v:ProcessAttributeReference, db: Session = Depends(get_reference_db)):
    create_process_attribute_reference_cross(db, v.process_id, v.picture_attribute_id, v.reference_value_presetting_type_id)
    return {"message": "Reference value presetting type created successfully"}


@router.put("/reference_update/{process_id}/{picture_attribute_id}")
def update_reference(v:ProcessAttributeReference, db: Session = Depends(get_reference_db)):
    reference = update_process_attribute_reference_cross(db, v.process_id, v.picture_attribute_id, v.reference_value_presetting_type_id)

    if reference:
        return reference
    else:
        return {"message": "Reference not found"}