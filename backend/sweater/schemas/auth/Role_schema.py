from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str


class RoleResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    user_id: str
    role_name: str


class RemoveRoleRequest(BaseModel):
    user_id: str
    role_name: str
