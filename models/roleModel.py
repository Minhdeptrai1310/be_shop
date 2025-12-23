from typing import List
from pydantic import BaseModel, Field


class RoleCreateSchema(BaseModel):
    name: str = Field(..., description="Role name, e.g. admin, user")

    class Config:
        json_schema_extra = {
            "example": {"name": "admin"}
        }


class RoleDataResponseBody(BaseModel):
    id: str = Field(...)
    name: str = Field(...)


class RoleResponseSchema(BaseModel):
    success: bool
    message: str
    data: RoleDataResponseBody


class GetAllRolesResponseSchema(BaseModel):
    success: bool
    message: str
    data: List[RoleDataResponseBody]
