from fastapi import HTTPException
from bson.objectid import ObjectId
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from database.entity.categoryEntity import Category


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    salePrice: Optional[float] = None
    category: str
    sizes: List[str]
    colors: List[str]
    stock: int
    images: List[str]
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    async def create_product(cls, name: str, description: str, price: float, category: str, 
                            sizes: List[str], colors: List[str], stock: int, images: List[str],
                            salePrice: Optional[float] = None, productEntity=None):
        current_time = datetime.now()
        product_data = {
            "name": name,
            "description": description,
            "price": price,
            "salePrice": salePrice,
            "category": category,
            "sizes": sizes,
            "colors": colors,
            "stock": stock,
            "images": images,
            "createdAt": current_time,
            "updatedAt": current_time
        }
        result = productEntity.insert_one(product_data)
        product_id = str(result.inserted_id)
        return cls(
            id=product_id,
            name=name,
            description=description,
            price=price,
            salePrice=salePrice,
            category=category,
            sizes=sizes,
            colors=colors,
            stock=stock,
            images=images,
            createdAt=current_time,
            updatedAt=current_time
        )

    @classmethod
    async def find_all_products(cls, productEntity):
        cursor = productEntity.find()
        products = []
        for document in cursor:
            cate = await Category.find_one_category_by_id(document.get("category"), categoryEntity=productEntity.database.categories)
            cat_name = cate.name if cate else document.get("category")
            product_id = str(document["_id"])
            item = cls(
                id=product_id,
                name=document.get("name"),
                description=document.get("description"),
                price=document.get("price"),
                salePrice=document.get("salePrice"),
                category=cat_name,
                sizes=document.get("sizes", []),
                colors=document.get("colors", []),
                stock=document.get("stock"),
                images=document.get("images", []),
                createdAt=document.get("createdAt"),
                updatedAt=document.get("updatedAt")
            )
            products.append(item.dict())
        return products

    @classmethod
    async def find_one_product_by_id(cls, product_id: str, productEntity):
        document = productEntity.find_one({"_id": ObjectId(product_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Product not found")
        return cls(
            id=str(document["_id"]),
            name=document.get("name"),
            description=document.get("description"),
            price=document.get("price"),
            salePrice=document.get("salePrice"),
            category=document.get("category"),
            sizes=document.get("sizes", []),
            colors=document.get("colors", []),
            stock=document.get("stock"),
            images=document.get("images", []),
            createdAt=document.get("createdAt"),
            updatedAt=document.get("updatedAt")
        )

    @classmethod
    async def update_product(cls, product_id: str, update_data: dict, productEntity):
        update_data["updatedAt"] = datetime.now()
        result = productEntity.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return await cls.find_one_product_by_id(product_id, productEntity)

    @staticmethod
    async def delete_product(product_id: str, productEntity):
        result = productEntity.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0

    @classmethod
    async def create_indexes(cls, db):
        collection = db.products
        collection.create_index("name")
        collection.create_index("category")
