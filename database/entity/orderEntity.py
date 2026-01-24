
from bson.objectid import ObjectId
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models.orderModel import OrderStatusEnum, OrderPaymentMethodEnum
from database.entity.userEntity import User

class OrderItemEntity(BaseModel):
    id: str
    orderId: str
    productId: str
    size: str
    color: str
    quantity: int
    price: int

class OrderEntity(BaseModel):
    id: str
    userId: str
    user_info: User
    orderCode: str
    totalAmount: int
    status: OrderStatusEnum
    paymentMethod: OrderPaymentMethodEnum
    paidAt: Optional[datetime] = None
    address: str
    orderItems: List[OrderItemEntity] = []
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    @classmethod
    async def create_order(
        cls,
        userId: str,
        user_info: User,
        totalAmount: int,
        paymentMethod: OrderPaymentMethodEnum,
        orderCode: str,
        address: str,
        orderEntity
    ):
        now = datetime.utcnow()
        order_data = {
            "userId": userId,
            "user_info": user_info.model_dump(),
            "orderCode": orderCode,
            "totalAmount": totalAmount,
            "status": OrderStatusEnum.PENDING_PAYMENT,
            "paymentMethod": paymentMethod,
            "address": address,
            "paidAt": None,
            "createdAt": now,
            "updatedAt": now,
        }

        result = orderEntity.insert_one(order_data)

        return cls(
            id=str(result.inserted_id),
            userId=userId,
            user_info=user_info,
            orderCode=orderCode,
            totalAmount=totalAmount,
            status=OrderStatusEnum.PENDING_PAYMENT,
            paymentMethod=paymentMethod,
            address=address,
            paidAt=None,
            orderItems=[],
            createdAt=now,
            updatedAt=now,
        )
    
    @classmethod
    async def get_all_orders(cls, db, order_items_db, user_db):
        all_order_doc = db.find()
        orders = []
        for doc in all_order_doc:
            order_id = str(doc['_id'])
            item = await cls.find_order_by_id(order_id, db, order_items_db, user_db)
            orders.append(item)
        return orders
    
    @classmethod
    async def get_orders_by_user_id(cls, user_id: str, db, order_items_db, user_db):
        order_docs = db.find({"userId": user_id})
        orders = []
        for doc in order_docs:
            order_id = str(doc['_id'])
            item = await cls.find_order_by_id(order_id, db, order_items_db, user_db)
            orders.append(item)
        return orders
    @classmethod
    async def find_order_by_id(cls, order_id: str, db, order_items_db, user_db):
        order_doc = db.find_one({"_id": ObjectId(order_id)})
        if not order_doc:
            raise HTTPException(status_code=404, detail="Order not found")

        user_info = user_db.find_one({'_id': ObjectId(order_doc['userId'])})
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")

        items_cursor = order_items_db.find({"orderId": ObjectId(order_id)})
        items = []

        for item in items_cursor:
            items.append(OrderItemEntity(
                id=str(item["_id"]),
                orderId=str(item["orderId"]),
                productId=item["productId"],
                size=item["size"],
                color=item["color"],
                quantity=item["quantity"],
                price=item["price"]
            ))

        return cls(
            id=str(order_doc["_id"]),
            userId=order_doc["userId"],
            user_info=User(
                id=str(user_info['_id']),
                name=user_info['name'],
                email=user_info['email'],
            ),
            orderCode=order_doc["orderCode"],
            totalAmount=order_doc["totalAmount"],
            status=order_doc["status"],
            paymentMethod=order_doc["paymentMethod"],
            address=order_doc["address"],
            paidAt=order_doc.get("paidAt"),
            orderItems=items,
            createdAt=order_doc.get("createdAt"),
            updatedAt=order_doc.get("updatedAt")
        )
    
    @classmethod
    async def confirm_payment(cls, order_id: str, orderEntity, orderItemEntity, userEntity):
        now = datetime.now()
        result = orderEntity.update_one(
            {"_id": ObjectId(order_id), "status": OrderStatusEnum.PENDING_PAYMENT},
            {
                "$set": {
                    "status": OrderStatusEnum.PAYMENT_CONFIRMED,
                    "paidAt": now
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=400, detail="Invalid order status")

        order_doc = await cls.find_order_by_id(order_id, orderEntity, orderItemEntity, userEntity)
        return order_doc
    
    @classmethod
    async def expire_orders(cls, orderEntity, hours: int = 24):
        threshold = datetime.now().timestamp() - hours * 3600
        orderEntity.update_many(
            {
                "status": OrderStatusEnum.PENDING_PAYMENT,
                "createdAt": {"$lt": datetime.fromtimestamp(threshold)}
            },
            {"$set": {"status": OrderStatusEnum.EXPIRED}}
        )
        
    @classmethod
    async def cancel_order(cls, order_id: str, orderEntity):
        """Hủy đơn hàng - chỉ hủy được nếu chưa thanh toán"""
        now = datetime.utcnow()
        result = orderEntity.update_one(
            {
                "_id": ObjectId(order_id),
                "status": {"$in": [OrderStatusEnum.PENDING_PAYMENT, OrderStatusEnum.EXPIRED]}
            },
            {
                "$set": {
                    "status": OrderStatusEnum.CANCELLED,
                    "updatedAt": now
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=400, 
                detail="Không thể hủy đơn hàng. Đơn hàng không tồn tại hoặc đã được thanh toán/xử lý."
            )
        
        return True



