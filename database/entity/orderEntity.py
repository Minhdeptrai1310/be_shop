
from bson.objectid import ObjectId
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models.orderModel import OrderStatusEnum, OrderPaymentMethodEnum

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
    orderCode: str
    totalAmount: int
    status: OrderStatusEnum
    paymentMethod: OrderPaymentMethodEnum
    paidAt: Optional[datetime] = None
    address: str
    orderItems: List[OrderItemEntity] = []

    @classmethod
    async def create_order(
        cls,
        userId: str,
        totalAmount: int,
        paymentMethod: OrderPaymentMethodEnum,
        orderCode: str,
        address: str,
        orderEntity
    ):
        order_data = {
            "userId": userId,
            "orderCode": orderCode,
            "totalAmount": totalAmount,
            "status": OrderStatusEnum.PENDING_PAYMENT,
            "paymentMethod": paymentMethod,
            "address": address,
            "paidAt": None
        }

        result = orderEntity.insert_one(order_data)

        return cls(
            id=str(result.inserted_id),
            userId=userId,
            orderCode=orderCode,
            totalAmount=totalAmount,
            status=OrderStatusEnum.PENDING_PAYMENT,
            paymentMethod=paymentMethod,
            address=address,
            paidAt=None,
            orderItems=[]
        )
    
    @classmethod
    async def find_order_by_id(cls, order_id: str, db, order_items_db):
        order_doc = db.find_one({"_id": ObjectId(order_id)})
        if not order_doc:
            raise HTTPException(status_code=404, detail="Order not found")

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
            orderCode=order_doc["orderCode"],
            totalAmount=order_doc["totalAmount"],
            status=order_doc["status"],
            paymentMethod=order_doc["paymentMethod"],
            address=order_doc["address"],
            paidAt=order_doc.get("paidAt"),
            orderItems=items
        )
    
    @classmethod
    async def confirm_payment(cls, order_id: str, orderEntity):
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

        return True
    
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



