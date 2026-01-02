
from typing import List
from pydantic import BaseModel, Field

class CartCreateSchema(BaseModel):
    userId: str = Field(..., description="User ID")
    productId: str = Field(..., description="Product ID")
    size: str
    color: str
    quantity: int

	# class Config:
	# 	json_schema_extra = {
	# 		"example": {
	# 			"name": "Áo Thun"
	# 		}
	# 	}

class CartDataResponseBody(BaseModel):
	id: str = Field(...)
	userId: str = Field(...)
	productId: str = Field(...)
	size: str = Field(...)
	color: str = Field(...)
	quantity: int = Field(...)

class CartResponseSchema(BaseModel):
	success: bool
	message: str
	data: CartDataResponseBody

class GetAllCartResponseSchema(BaseModel):
	success: bool
	message: str
	data: List[CartDataResponseBody]