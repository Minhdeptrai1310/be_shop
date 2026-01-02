from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatusEnum(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class OrderPaymentMethodEnum(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    MONEY_TRANSFER = "MONEY_TRANSFER"

class OrderCreateSchema(BaseModel):
    userId: str = Field(...)
    paymentMethod: OrderPaymentMethodEnum = Field(...)
    address: str

class OrderItemDataResponse(BaseModel):
    id: str = Field(...)
    orderId: str = Field(...)
    productId: str = Field(...)
    size: str = Field(...)
    color: str = Field(...)
    quantity: int = Field(...)
    price: int = Field(...)

class OrderDataResponse(BaseModel):
    id: str = Field(...)
    userId: str = Field(...)
    orderCode: str = Field(...)
    totalAmount: int = Field(...)
    status: OrderStatusEnum
    paymentMethod: OrderPaymentMethodEnum
    paidAt: Optional[datetime]
    address: str
    orderItems: List[OrderItemDataResponse]

class OrderResponseSchema(BaseModel):
    success: bool
    message: str
    data: OrderDataResponse