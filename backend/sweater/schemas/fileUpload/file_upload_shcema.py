from pydantic import BaseModel
from typing import List, Optional, Dict

class UploadResponse(BaseModel):
    ok: bool
    message: str
    inserted_rows: int

class UploadFile(BaseModel):
    filename: str
    content_type: str

class MissingReferenceValue(BaseModel):
    type_id: str
    type_name: str
    column: str
    value: str

class ValidationRequiredResponse(BaseModel):
    status: str  # "needs_validation"
    missing_values: List[MissingReferenceValue]
    existing_values_by_type: Dict[str, List[str]]  # type_id -> list of existing values

class ConfirmDecision(BaseModel):
    type_id: str
    column: str
    original_value: str
    save: bool
    replace_with: Optional[str] = None