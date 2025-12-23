from fastapi import HTTPException
from bson.objectid import ObjectId
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr
from datetime import datetime
from database.collections import init_db
import base64
# from bas64, md5


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    password: str
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    async def create_user(cls, name: str, email: str, password: str, userEntity):
        # NOTE: base64 is reversible and not suitable for password hashing in production.
        # Kept as-is to match existing code pattern; consider replacing with a secure hash.
        hashed_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
        current_time = datetime.now()
        user_data = {
            "name": name,
            "email": email,
            "role": "user",
            "password": hashed_password,
            "createdAt": current_time,
            "updatedAt": current_time
        }
        result = userEntity.insert_one(user_data)
        user_id = str(result.inserted_id)
        return cls(id=user_id, name=name, email=email, role="user", password=hashed_password, createdAt=current_time, updatedAt=current_time)

    @staticmethod
    async def delete_user(user_id: str, userEntity):
        result = await userEntity.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @classmethod
    async def find_all_users(self, userEntity):
        cursor = userEntity.find()
        users = []
        for document in cursor:
            user_id = str(document["_id"])
            item = self(
                id=user_id,
                name=document["name"],
                email=document["email"],
                role=document.get("role", "user"),
                password=document["password"],
                createdAt=document["createdAt"],
                updatedAt=document["updatedAt"]
            )
            users.append(item.dict())
        return users

    @classmethod
    async def find_one_user_by_id(cls, user_id: str, userEntity):
        document = userEntity.find_one({"_id": ObjectId(user_id)})
        if not document:
            raise HTTPException(status_code=404, detail="User not found")
        return cls(
            id=str(document["_id"]),
            name=document["name"],
            email=document["email"],
            role=document.get("role", "user"),
            password=document["password"],
            createdAt=document["createdAt"],
            updatedAt=document["updatedAt"]
        )

    @classmethod
    async def find_one_user_by_email(cls, user_email: str, userEntity):
        print("Finding user by email:", userEntity)
        return userEntity.find_one({"email": user_email})

    @staticmethod
    async def update_user(user_id: str, name: str, email: str, userEntity):
        current_time = datetime.now()
        update_data = {"name": name, "email": email, "updatedAt": current_time}
        result = userEntity.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return True

    # Create indexes on id and email fields
    @staticmethod
    async def create_indexes(db):
        db["users"].create_index("id")
        db["users"].create_index("email", unique=True)
