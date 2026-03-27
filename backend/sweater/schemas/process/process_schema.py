from pydantic import BaseModel

class UpdateProcess(BaseModel):
    id: str
    title: str
    description: str

class CreateProcess(BaseModel):
    title: str
    description: str