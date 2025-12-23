from typing import List, Optional
from pydantic import BaseModel, Field


class ProductCreateSchema(BaseModel):
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Product price")
    salePrice: Optional[float] = Field(None, description="Sale price (optional)")
    category: str = Field(..., description="Product category")
    sizes: List[str] = Field(..., description="Available sizes")
    colors: List[str] = Field(..., description="Available colors")
    stock: int = Field(..., description="Stock quantity")
    images: List[str] = Field(..., description="Product images")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Áo Thun Nam",
                "description": "Áo thun nam chất lượng cao",
                "price": 150000,
                "salePrice": 99000,
                "category": "áo thun",
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Đen", "Trắng", "Xanh"],
                "stock": 50,
                "images": ["image1.jpg", "image2.jpg"]
            }
        }


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[float] = Field(None, description="Product price")
    salePrice: Optional[float] = Field(None, description="Sale price")
    category: Optional[str] = Field(None, description="Product category")
    sizes: Optional[List[str]] = Field(None, description="Available sizes")
    colors: Optional[List[str]] = Field(None, description="Available colors")
    stock: Optional[int] = Field(None, description="Stock quantity")
    images: Optional[List[str]] = Field(None, description="Product images")

    class Config:
        json_schema_extra = {
            "example": {
                "price": 120000,
                "salePrice": 79000,
                "stock": 45
            }
        }


class ProductDataResponseBody(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    price: float = Field(...)
    salePrice: Optional[float] = Field(...)
    category: str = Field(...)
    sizes: List[str] = Field(...)
    colors: List[str] = Field(...)
    stock: int = Field(...)
    images: List[str] = Field(...)


class ProductResponseSchema(BaseModel):
    success: bool
    message: str
    data: ProductDataResponseBody


class GetAllProductsResponseSchema(BaseModel):
    success: bool
    message: str
    data: List[ProductDataResponseBody]
