from pydantic import BaseModel, Field, EmailStr


class UserRegisterSchema(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    print("UserRegisterSchema:", username, email, password)
    class Config:
        json_schema_extra = {
            "example": {
                "username": "user1",
                "email": "user@test.com",
                "password": "weakpassword"
            }
        }

class RegisterDataResponseBody(BaseModel):
    id: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...) 

class UserRegisterResponseSchema(BaseModel):
    success: bool 
    message: str 
    data: RegisterDataResponseBody 
        
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(...)
    new_password: str = Field(...)

class GoogleTokenRequest(BaseModel):
    token: str

class ForgotPasswordRequest(BaseModel):
    email: str


