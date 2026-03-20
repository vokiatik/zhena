from pydantic import BaseModel

class UploadResponse(BaseModel):
    ok: bool
    message: str
    inserted_rows: int

class UploadFile(BaseModel):
    filename: str
    content_type: str