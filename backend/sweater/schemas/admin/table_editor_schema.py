from pydantic import BaseModel
from typing import Any


class TableSettingUpdate(BaseModel):
    visible: bool
    only_admin: bool
    editable: bool


class RowUpdateRequest(BaseModel):
    data: dict[str, Any]


class RowCreateRequest(BaseModel):
    data: dict[str, Any]
