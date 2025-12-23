from fastapi import HTTPException
from bson.objectid import ObjectId
from pydantic import BaseModel
from datetime import datetime


class Role(BaseModel):
    id: str
    name: str

    @classmethod
    async def create_role(cls, name: str, roleEntity):
        role_data = {"name": name}
        result = roleEntity.insert_one(role_data)
        role_id = str(result.inserted_id)
        return cls(id=role_id, name=name)

    @staticmethod
    async def delete_role(role_id: str, roleEntity):
        result = await roleEntity.delete_one({"_id": ObjectId(role_id)})
        return result.deleted_count > 0

    @classmethod
    async def find_all_roles(self, roleEntity):
        cursor = roleEntity.find()
        roles = []
        for document in cursor:
            r_id = str(document["_id"])
            item = self(id=r_id, name=document.get("name"))
            roles.append(item.dict())
        return roles

    @classmethod
    async def find_one_role_by_id(cls, role_id: str, roleEntity):
        document = roleEntity.find_one({"_id": ObjectId(role_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Role not found")
        return cls(id=str(document["_id"]), name=document.get("name"))

    @staticmethod
    async def update_role(role_id: str, name: str | None, roleEntity=None):
        update_data = {}
        if name is not None:
            update_data["name"] = name
        result = roleEntity.update_one({"_id": ObjectId(role_id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Role not found")
        return True

    @staticmethod
    async def create_indexes(db):
        db["roles"].create_index("name", unique=True)
