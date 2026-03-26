from pydantic import BaseModel

class Attribute(BaseModel):
    id: str
    reference_value: str
    reference_value_presetting_type_id: str
    created_at: str

class ProcessAttribute(BaseModel):
    id: str
    title: str
    is_shown: bool
    is_editable: bool
    reference_value: str = None
    reference_value_presetting_type_id: str = None
    created_at: str
    process_id: str

class ProcessAttributeCross(BaseModel):
    picture_attribute_id: str
    reference_value_presetting_type_id: str

class ProcessAttributeReference(BaseModel):
    process_id: str
    picture_attribute_id: str
    reference_value_presetting_type_id: str