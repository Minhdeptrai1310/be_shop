from fastapi import HTTPException
from bson.objectid import ObjectId
from pydantic import BaseModel
from datetime import datetime
import re
from typing import Optional


class Category(BaseModel):
    id: str
    name: Optional[str]
    slug: Optional[str]

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from category name"""
        # Convert to lowercase
        slug = name.lower()
        # Replace Vietnamese characters
        slug = slug.replace('á', 'a').replace('à', 'a').replace('ả', 'a').replace('ã', 'a').replace('ạ', 'a')
        slug = slug.replace('é', 'e').replace('è', 'e').replace('ẻ', 'e').replace('ẽ', 'e').replace('ẹ', 'e')
        slug = slug.replace('í', 'i').replace('ì', 'i').replace('ỉ', 'i').replace('ĩ', 'i').replace('ị', 'i')
        slug = slug.replace('ó', 'o').replace('ò', 'o').replace('ỏ', 'o').replace('õ', 'o').replace('ọ', 'o')
        slug = slug.replace('ú', 'u').replace('ù', 'u').replace('ủ', 'u').replace('ũ', 'u').replace('ụ', 'u')
        slug = slug.replace('ý', 'y').replace('ỳ', 'y').replace('ỷ', 'y').replace('ỹ', 'y').replace('ỵ', 'y')
        slug = slug.replace('đ', 'd')
        # Remove special characters and replace spaces with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        # Remove leading and trailing hyphens
        slug = slug.strip('-')
        return slug


    @classmethod
    async def create_category(cls, name: str, categoryEntity):
        slug = cls.generate_slug(name)
        category_data = {
            "name": name,
            "slug": slug
        }
        result = categoryEntity.insert_one(category_data)
        category_id = str(result.inserted_id)
        return cls(id=category_id, name=name, slug=slug)

    @staticmethod
    async def delete_category(category_id: str, categoryEntity):
        result = await categoryEntity.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0


    @classmethod
    async def find_all_categories(self, categoryEntity):
        cursor = categoryEntity.find()
        categories = []
        for document in cursor:
            cat_id = str(document["_id"])
            item = self(
                id=cat_id,
                name=document.get("name"),
                slug=document.get("slug")
            )
            categories.append(item.dict())
        return categories


    @classmethod
    async def find_one_category_by_id(cls, category_id: str, categoryEntity):
        document = categoryEntity.find_one({"_id": ObjectId(category_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Category not found")
        return cls(
            id=str(document["_id"]),
            name=document.get("name"),
            slug=document.get("slug")
        )

    @classmethod
    async def find_one_category_by_slug(cls, slug: str, categoryEntity):
        document = categoryEntity.find_one({"slug": slug})
        if not document:
            raise HTTPException(status_code=404, detail="Category not found")
        return cls(
            id=str(document["_id"]),
            name=document.get("name"),
            slug=document.get("slug")
        )


    @staticmethod
    async def update_category(category_id: str, name: str | None, categoryEntity=None):
        update_data = {}
        if name is not None:
            update_data["name"] = name
            update_data["slug"] = Category.generate_slug(name)
        result = categoryEntity.update_one({"_id": ObjectId(category_id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        return True


    @staticmethod
    async def create_indexes(db):
        db["categories"].create_index("id")
        db["categories"].create_index("slug", unique=True)
#  verify request FE xong lưu database