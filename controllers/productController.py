from fastapi import HTTPException
from models.productModel import ProductCreateSchema, ProductUpdateSchema
from database.entity.productEntity import Product
from util.ResponseSchema import successResponse, errorResponse


async def createProductController(payload: ProductCreateSchema, productEntity):
    try:
        product = await Product.create_product(
            name=payload.name,
            description=payload.description,
            price=payload.price,
            salePrice=payload.salePrice,
            category=payload.category,
            sizes=payload.sizes,
            colors=payload.colors,
            stock=payload.stock,
            images=payload.images,
            featured=payload.featured,
            productEntity=productEntity
        )
        return successResponse("Product created successfully", product.dict())
    except Exception as e:
        return errorResponse("Failed to create product", str(e))


async def getProductController(product_id: str, productEntity):
    try:
        product = await Product.find_one_product_by_id(product_id, productEntity)
        return successResponse("Product retrieved successfully", product.dict())
    except HTTPException as e:
        return errorResponse(e.detail, None, e.status_code)
    except Exception as e:
        return errorResponse("Failed to retrieve product", str(e), 500)


async def getAllProductsController(productEntity):
    try:
        products = await Product.find_all_products(productEntity)
        return successResponse("Products retrieved successfully", products)
    except Exception as e:
        return errorResponse("Failed to retrieve products", str(e), 500)


async def updateProductController(product_id: str, payload: ProductUpdateSchema, productEntity):
    try:
        # Only include fields that are provided
        update_data = {k: v for k, v in payload.dict().items() if v is not None}
        
        if not update_data:
            return errorResponse("No fields to update", None, 400)
        
        product = await Product.update_product(product_id, update_data, productEntity)
        return successResponse("Product updated successfully", product.dict())
    except HTTPException as e:
        return errorResponse(e.detail, None, e.status_code)
    except Exception as e:
        return errorResponse("Failed to update product", str(e), 500)


async def deleteProductController(product_id: str, productEntity):
    try:
        success = await Product.delete_product(product_id, productEntity)
        if success:
            return successResponse("Product deleted successfully", None)
        else:
            return errorResponse("Product not found", None, 404)
    except Exception as e:
        return errorResponse("Failed to delete product", str(e), 500)
