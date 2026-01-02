from fastapi import APIRouter, Depends, Path, Body
from database.collections import get_user_collection, get_mail_collection
from models.authModel import UserLoginSchema, UserRegisterSchema, UserRegisterResponseSchema, GoogleTokenRequest, ChangePasswordRequest, ForgotPasswordRequest
from controllers.authController import registerController, loginController, googleLoginController, changePasswordController, forgotPassword

auth = APIRouter()


@auth.post('/register', response_model=UserRegisterResponseSchema)
async def register(user: UserRegisterSchema, userEntity=Depends(get_user_collection)):
    return await registerController(user.username, user.email, user.password, userEntity)

@auth.post('/login')
async def login(user: UserLoginSchema, userEntity=Depends(get_user_collection)):
    return await loginController(user.email, user.password, userEntity)

@auth.post('/{user_id}/change_password')
async def changePassword(user_id: str = Path(...), payload: ChangePasswordRequest = Body(...), userEntity=Depends(get_user_collection)):
    return await changePasswordController(user_id, payload.old_password, payload.new_password, userEntity)

@auth.post('/login/google')
async def loginGoogle(request: GoogleTokenRequest, userEntity=Depends(get_user_collection)):
    return await googleLoginController(request, userEntity)

@auth.post('/forget_password')
async def forgot_password(payload: ForgotPasswordRequest, userEntity=Depends(get_user_collection), emailEntity=Depends(get_mail_collection)):
    return await forgotPassword(payload.email, userEntity, emailEntity)
