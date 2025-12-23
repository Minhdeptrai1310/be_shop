from fastapi import APIRouter, Depends, Path
from database.collections import get_role_collection
from models.roleModel import (
    RoleCreateSchema,
    RoleResponseSchema,
    GetAllRolesResponseSchema,
)
from controllers.roleController import (
    createRoleController,
    getAllRolesController,
    getRoleController,
    updateRoleController,
    deleteRoleController,
)

role = APIRouter()


@role.post('/', response_model=RoleResponseSchema)
async def create_role(payload: RoleCreateSchema, roleEntity=Depends(get_role_collection)):
    return await createRoleController(payload, roleEntity)


@role.get('/', response_model=GetAllRolesResponseSchema)
async def list_roles(roleEntity=Depends(get_role_collection)):
    return await getAllRolesController(roleEntity)


@role.get('/{role_id}', response_model=RoleResponseSchema)
async def get_role(role_id: str = Path(...), roleEntity=Depends(get_role_collection)):
    return await getRoleController(role_id, roleEntity)


@role.put('/{role_id}', response_model=RoleResponseSchema)
async def update_role(role_id: str, payload: RoleCreateSchema, roleEntity=Depends(get_role_collection)):
    return await updateRoleController(role_id, payload, roleEntity)


@role.delete('/{role_id}')
async def delete_role(role_id: str, roleEntity=Depends(get_role_collection)):
    return await deleteRoleController(role_id, roleEntity)
