from database.entity.roleEntity import Role
from fastapi import HTTPException, status
from util.ResponseSchema import successResponse, errorResponse


async def createRoleController(payload, roleEntity):
    try:
        new_role = await Role.create_role(name=payload.name, roleEntity=roleEntity)
        return successResponse("Role created", new_role.dict())
    except Exception as ex:
        print("exception under Role create controller:", ex)
        # if duplicate key, roleEntity will raise; return friendly error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errorResponse("Role creation failed"))


async def getAllRolesController(roleEntity):
    try:
        roles = await Role.find_all_roles(roleEntity)
        return successResponse("Roles fetched", roles)
    except Exception as ex:
        print("exception under getAllRoles:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def getRoleController(role_id: str, roleEntity):
    try:
        role = await Role.find_one_role_by_id(role_id, roleEntity)
        return successResponse("Role fetched", role.dict())
    except HTTPException:
        raise
    except Exception as ex:
        print("exception under getRole:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def updateRoleController(role_id: str, payload, roleEntity):
    try:
        await Role.update_role(role_id=role_id, name=payload.name if hasattr(payload, 'name') else None, roleEntity=roleEntity)
        return successResponse("Role updated", {"id": role_id})
    except HTTPException:
        raise
    except Exception as ex:
        print("exception under updateRole:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def deleteRoleController(role_id: str, roleEntity):
    try:
        deleted = await Role.delete_role(role_id, roleEntity)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=errorResponse("Role not found"))
        return successResponse("Role deleted", {"id": role_id})
    except HTTPException:
        raise
    except Exception as ex:
        print("exception under deleteRole:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))
