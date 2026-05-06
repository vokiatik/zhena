from pydantic import BaseModel


class VerifyRequest(BaseModel):
    id: str
    url: str
    process_id: str
    extra: dict[str, str] = {}


class DeclineRequest(BaseModel):
    id: str
    process_id: str
