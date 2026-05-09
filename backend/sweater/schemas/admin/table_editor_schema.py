from pydantic import BaseModel
from typing import Any


class TableSettingUpdate(BaseModel):
    visible: bool
    only_admin: bool
    editable: bool
    uploadable: bool = False
    upload_prefix: str | None = None


class RowUpdateRequest(BaseModel):
    data: dict[str, Any]


class RowCreateRequest(BaseModel):
    data: dict[str, Any]
