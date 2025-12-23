from fastapi import APIRouter, Depends, Path
from database.collections import get_product_collection
from models.productModel import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductResponseSchema,
    GetAllProductsResponseSchema,
)
from controllers.productController import (
    createProductController,
    getAllProductsController,
    getProductController,
    updateProductController,
    deleteProductController,
)

product = APIRouter()


@product.post('/', response_model=ProductResponseSchema)
async def create_product(payload: ProductCreateSchema, productEntity=Depends(get_product_collection)):
    return await createProductController(payload, productEntity)


@product.get('/', response_model=GetAllProductsResponseSchema)
async def list_products(productEntity=Depends(get_product_collection)):
    return await getAllProductsController(productEntity)


@product.get('/{product_id}', response_model=ProductResponseSchema)
async def get_product(product_id: str = Path(...), productEntity=Depends(get_product_collection)):
    return await getProductController(product_id, productEntity)


@product.put('/{product_id}', response_model=ProductResponseSchema)
async def update_product(product_id: str, payload: ProductUpdateSchema, productEntity=Depends(get_product_collection)):
    return await updateProductController(product_id, payload, productEntity)


@product.delete('/{product_id}')
async def delete_product(product_id: str, productEntity=Depends(get_product_collection)):
    return await deleteProductController(product_id, productEntity)
