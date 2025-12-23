import base64
from bson import ObjectId 
from database.entity.userEntity import User
from fastapi import HTTPException, status
from util.ResponseSchema import successResponse, errorResponse
from database.entity.userEntity import User
from auth.tokenGenerator import generateToken
from passlib.hash import bcrypt
from datetime import datetime, timedelta, timezone

async def registerController(name: str, email: str, password: str, db):
    user = await User.find_one_user_by_email(email, db)
    if user:
        response = errorResponse("User with this email exist")
        print("user not found:", response)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=response)
    try:
        users_collection = db["users"]
        new_user = await User.create_user(name=name, email=email, password=password, userEntity=users_collection)
        return successResponse("User Registered", {
            "id": str(new_user.id),
            "username": new_user.name,
            "email": new_user.email,
        })
    except Exception as ex:
        print("exception under Register controller:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=errorResponse("Internal Server Error"))


async def loginController(email: str, password: str, db):
    db_user = await User.find_one_user_by_email(email, db["users"])
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
            }
        })
    except Exception as e:
        print("exception under Login controller:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse(
            "Internal Server Error"), headers={"X-Error": str(e)})


async def updateProfileController(user_id: str, full_name: str, phone: str, db):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail=errorResponse("Thiếu thông tin User ID"))
            
        users_collection = db["users"]
        
        # 1. Kiểm tra định dạng ID (Tránh lỗi crash server nếu ID sai định dạng)
        try:
            oid = ObjectId(user_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=errorResponse("ID người dùng không hợp lệ"))

        # 2. Kiểm tra người dùng có tồn tại không
        db_user = await users_collection.find_one({"_id": oid})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=errorResponse("Người dùng không tồn tại trong hệ thống")
            )

        # 3. Tiến hành cập nhật
        # Lưu ý: 'name' trong DB tương ứng với 'fullName' ở FE
        update_data = {
            "name": full_name,
            "phone": phone
        }
        
        await users_collection.update_one(
            {"_id": oid},
            {"$set": update_data}
        )

        # 4. Lấy lại dữ liệu mới nhất để đồng bộ hóa cho Frontend
        updated_user = await users_collection.find_one({"_id": oid})
        
        return successResponse("Cập nhật thông tin thành công", {
            "id": str(updated_user['_id']),
            "fullName": updated_user['name'],
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
        # 1. Truy cập collection users
        users_collection = db["users"]
        
        # 2. Tìm người dùng trong database theo ID (ép kiểu ObjectId nếu cần)
        from bson import ObjectId
        db_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=errorResponse("Người dùng không tồn tại")
            )

        # 3. Kiểm tra mật khẩu hiện tại (Giải mã Base64 tương tự loginController)
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

        # 4. Mã hóa mật khẩu mới sang Base64
        new_password_encoded = base64.b64encode(new_password.encode('utf-8')).decode('utf-8')

        # 5. Cập nhật mật khẩu mới vào MongoDB
        result = await users_collection.update_one(
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