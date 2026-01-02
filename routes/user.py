from fastapi import APIRouter, Depends, Path, Body
from database.collections import get_user_collection
from models.userModel import (GetAllUserResponseSchema, UpdateDataResponseBody)
from database.entity.userEntity import User
from util.ResponseSchema import successResponse
from controllers.authController import updateProfileController

user = APIRouter()


@user.get('/', response_model=GetAllUserResponseSchema)
async def find_all_users(userEntity=Depends(get_user_collection)):
    # print("current_user:", current_user)
    data = await User.find_all_users(userEntity)
    return successResponse("All Users " + str(len(data)), data)

@user.put('/{id}/profile')
async def update_profile(id: str = Path(...), payload: UpdateDataResponseBody = Body(...), userEntity=Depends(get_user_collection)):
    return await updateProfileController(user_id=id, payload=payload, db=userEntity)
