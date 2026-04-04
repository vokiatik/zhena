from pydantic import BaseModel

class CreateReference(BaseModel):
    value: str

class UpdateReference(BaseModel):
    id: str
    value: str