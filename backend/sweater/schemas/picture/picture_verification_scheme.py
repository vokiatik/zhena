from pydantic import BaseModel

class VerifyRequest(BaseModel):
    id: str
    url: str
    extra: dict[str, str] = {}
