import base64
from bson import ObjectId 
from database.entity.userEntity import User
from fastapi import HTTPException, status
from util.ResponseSchema import successResponse, errorResponse
from database.entity.userEntity import User
from auth.tokenGenerator import generateToken
from passlib.hash import bcrypt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests
from models.authModel import GoogleTokenRequest
from config.globals import GOOGLE_CLIENT_ID
from models.userModel import UpdateDataResponseBody
from controllers.emailController import send_mail, SendMailDTO
import secrets
import string
import jwt

async def registerController(name: str, email: str, password: str, phone: str, db):
    user = await User.find_one_user_by_email(email, db)
    if user:
        response = errorResponse("User with this email exist")
        print("user not found:", response)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=response)
    try:
        users_collection = db
        new_user = await User.create_user(name=name, email=email, password=password, phone=phone, userEntity=users_collection)
        return successResponse("User Registered", {
            "id": str(new_user.id),
            "username": new_user.name,
            "email": new_user.email,
            "phone": new_user.phone
        })
    except Exception as ex:
        print("exception under Register controller:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=errorResponse("Internal Server Error"))
    
async def googleLoginController(request: GoogleTokenRequest, db):
    try:
        # Xác thực Google token
        idinfo = id_token.verify_oauth2_token(
            request.token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=60
        )

        # Lấy thông tin từ Google
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        picture = idinfo.get('picture', '')

        # Kiểm tra user đã tồn tại chưa
        users_collection = db
        existing_user = users_collection.find_one({"google_id": google_id})
        is_new_user = False

        if existing_user:
            # Cập nhật last_login
            users_collection.update_one(
                {"google_id": google_id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            user_id = str(existing_user["_id"])
            print(f"✅ User đăng nhập lại: {email}")
        else:
            # Tạo user mới
            new_user = {
                "google_id": google_id,
                "email": email,
                "name": name,
                "picture": picture,
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow()
            }
            result = users_collection.insert_one(new_user)
            user_id = str(result.inserted_id)
            is_new_user = True
            print(f"✅ User mới được tạo: {email}")

        # Lấy thông tin user đầy đủ
        user = users_collection.find_one({"google_id": google_id})
        
        # Tạo JWT token
        token = generateToken({"_id": user_id, "exp": datetime.now(
            tz=timezone.utc) + timedelta(days=2)})
        
        payload = jwt.decode(token, options={"verify_signature": False})
        token_expire = payload["exp"]

        return {
            "success": True,
            "token": token,
            "token_expire": token_expire,
            "is_new_user": is_new_user,
            "user": {
                "id": str(user["_id"]),
                "google_id": user["google_id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user["picture"],
                "created_at": user["created_at"].isoformat(),
                "last_login": user["last_login"].isoformat()
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ: {str(e)}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi server")


async def loginController(email: str, password: str, db):
    db_user = await User.find_one_user_by_email(email, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errorResponse(
            "User with this email does not exist"))
    try:
        isMatched = base64.b64decode(db_user['password']).decode('utf-8') == password
        if not isMatched:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=errorResponse("Invalid password"))

        token = generateToken({"_id": str(db_user['_id']), "exp": datetime.now(
            tz=timezone.utc) + timedelta(days=2)})
        return successResponse("User Logged In", {
            "access_token": token,
            "token_expire": datetime.now(
            tz=timezone.utc) + timedelta(days=2),
            "user": {
                "id": str(db_user['_id']),
                "name": db_user['name'],
                "email": db_user['email'],
                "role": db_user['role'],
                "phone": db_user['phone']
            }
        })
    except Exception as e:
        print("exception under Login controller:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse(
            "Internal Server Error"), headers={"X-Error": str(e)})


async def updateProfileController(user_id: str, payload: UpdateDataResponseBody, db):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail=errorResponse("Thiếu thông tin User ID"))
            
        users_collection = db
        
        try:
            oid = ObjectId(user_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=errorResponse("ID người dùng không hợp lệ"))

        db_user = users_collection.find_one({"_id": oid})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=errorResponse("Người dùng không tồn tại trong hệ thống")
            )

        update_data = {
            "name": payload.name,
            "phone": payload.phone
        }
        
        users_collection.update_one(
            {"_id": oid},
            {"$set": update_data}
        )

        updated_user = users_collection.find_one({"_id": oid})
        
        return successResponse("Cập nhật thông tin thành công", {
            "id": str(updated_user['_id']),
            "name": updated_user['name'],
            "email": updated_user['email'],
            "phone": updated_user.get('phone', ''),
            "role": updated_user.get('role', 'customer'),
            "createdAt": str(updated_user.get('createdAt', ''))
        })

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error in updateProfileController: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=errorResponse("Lỗi hệ thống nội bộ khi cập nhật profile")
        )

async def changePasswordController(user_id: str, current_password: str, new_password: str, db):
    try:
        users_collection = db
        
        from bson import ObjectId
        db_user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=errorResponse("Người dùng không tồn tại")
            )

        try:
            stored_password = base64.b64decode(db_user['password']).decode('utf-8')
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=errorResponse("Lỗi định dạng mật khẩu cũ trên hệ thống")
            )

        if stored_password != current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=errorResponse("Mật khẩu hiện tại không chính xác")
            )

        new_password_encoded = base64.b64encode(new_password.encode('utf-8')).decode('utf-8')

        result = users_collection.update_one(
            {"_id": db_user["_id"]},
            {"$set": {"password": new_password_encoded}}
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=errorResponse("Không có thay đổi nào được thực hiện")
            )

        return successResponse("Mật khẩu đã được cập nhật thành công", None)

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error in changePasswordController: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=errorResponse("Lỗi hệ thống nội bộ")
        )
        
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_password(length: int = 10):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


async def forgotPassword(email: str, db, emailDb):
    users_collection = db
    db_user = users_collection.find_one({"email": email})

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=errorResponse("Email chưa được đăng ký!"),
        )

    new_password = generate_password()
    print(new_password)

    hashed_password = base64.b64encode(new_password.encode('utf-8')).decode('utf-8')
    
    users_collection.update_one(
        {"_id": db_user["_id"]},
        {"$set": {"password": hashed_password}},
    )

    mail_data = SendMailDTO(
        to=email,
        subject="Mật khẩu mới của bạn",
        content=f"Mật khẩu mới của bạn là: {new_password}"
    )

    await send_mail(
        mail_data,
        emailDb
    )

    return successResponse("Mật khẩu mới đã được gửi về email")