# cartEntity.py
from pydantic import BaseModel
from bson import ObjectId

class CartEntity(BaseModel):
    id: str
    userId: str
    productId: str
    size: str
    color: str
    quantity: int

    @classmethod
    async def create_cart(cls, userId: str, productId: str, size: str, color: str, quantity: int, cartEntity):
        existing_item = await cls.find_one_cart_by_product(userId, productId, size, color, cartEntity)
        if (existing_item):
            cartEntity.update_one(
                {"_id": ObjectId(existing_item.id)},
                {"$inc": {"quantity": quantity}},
            )
            doc = cartEntity.find_one({"_id": ObjectId(existing_item.id)})
            return cls(
                id=str(doc["_id"]),
                userId=doc["userId"],
                productId=doc["productId"],
                size=doc["size"],
                color=doc["color"],
                quantity=doc["quantity"],
            )
        data = {
            "userId": userId,
            "productId": productId,
            "size": size,
            "color": color,
            "quantity": quantity
        }
        result = cartEntity.insert_one(data)
        return cls(id=str(result.inserted_id), **data)

    @staticmethod
    async def delete_cart(cart_id: str, cartEntity):
        result = cartEntity.delete_one({"_id": ObjectId(cart_id)})
        return result.deleted_count > 0

    @classmethod
    async def find_all_carts(cls, cartEntity):
        carts = []
        for doc in cartEntity.find():
            carts.append(
                cls(
                    id=str(doc["_id"]),
                    userId=doc.get("userId"),
                    productId=doc.get("productId"),
                    size=doc.get("size"),
                    color=doc.get("color"),
                    quantity=doc.get("quantity")
                ).dict()
            )
        return carts
    
    @classmethod
    async def find_all_carts_by_userId(cls, user_id: str, cartEntity):
        cursor = cartEntity.find({"userId": user_id})
        carts = []
        for doc in cursor:
            cart_id = str(doc["_id"])
            item = cls(
                id=cart_id,
                userId=doc.get("userId"),
                productId=doc.get("productId"),
                size=doc.get("size"),
                color=doc.get("color"),
                quantity=doc.get("quantity")
            )
            carts.append(item.dict())
        return carts

    @classmethod
    async def find_one_cart_by_id(cls, cart_id: str, cartEntity):
        doc = cartEntity.find_one({"_id": ObjectId(cart_id)})
        if not doc:
            return None
        return cls(
            id=str(doc["_id"]),
            userId=doc.get("userId"),
            productId=doc.get("productId"),
            size=doc.get("size"),
            color=doc.get("color"),
            quantity=doc.get("quantity")
        )

    @classmethod
    async def find_one_cart_by_product(cls, userId: str, productId: str, size: str, color: str, cartEntity):
        doc = cartEntity.find_one(
            {
                "userId": userId,
                "productId": productId,
                "size": size,
                "color": color,
            }
        )
        if not doc:
            return None
        return cls(
            id=str(doc["_id"]),
            userId=doc["userId"],
            productId=doc["productId"],
            size=doc["size"],
            color=doc["color"],
            quantity=doc["quantity"],
        )
    
    @classmethod
    async def update_cart_by_id(
        cls,
        cart_id: str,
        userId: str,
        productId: str,
        size: str,
        color: str,
        quantity: int,
        cartEntity,
    ):
        cartEntity.update_one(
            {"_id": ObjectId(cart_id)},
            {
                "$set": {
                    "userId": userId,
                    "productId": productId,
                    "size": size,
                    "color": color,
                    "quantity": quantity,
                }
            },
        )

        doc = cartEntity.find_one({"_id": ObjectId(cart_id)})
        if not doc:
            return None

        return cls(
            id=str(doc["_id"]),
            userId=doc["userId"],
            productId=doc["productId"],
            size=doc["size"],
            color=doc["color"],
            quantity=doc["quantity"],
        )