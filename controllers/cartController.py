# cartController.py
from database.entity.cartEntity import CartEntity
from models.cartModel import CartCreateSchema
from fastapi import HTTPException, status
from util.ResponseSchema import successResponse, errorResponse

async def create_cart(payload: CartCreateSchema, cartCollection):
    try:
        cart = await CartEntity.create_cart(
            userId=payload.userId,
            productId=payload.productId,
            size=payload.size,
            color=payload.color,
            quantity=payload.quantity,
            cartEntity=cartCollection
        )
        return successResponse("Cart created", cart.dict())
    except Exception as ex:
        print("exception under Cart create controller:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))
    
async def update_cart(id: str, payload:CartCreateSchema, cartCollection):
    try:
        cart = await CartEntity.update_cart_by_id(
            cart_id=id,
            userId=payload.userId,
            productId=payload.productId,
            size=payload.size,
            color=payload.color,
            quantity=payload.quantity,
            cartEntity=cartCollection
        )
        return successResponse("Cart updated", cart.dict())
    except Exception as ex:
        print("exception under Cart update controller:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))
    
async def get_all_carts(cartCollection):
    return await CartEntity.find_all_carts(cartCollection)

async def get_all_carts_by_userId(user_id: str, cartCollection):
    try:
        cart = await CartEntity.find_all_carts_by_userId(user_id, cartCollection)
        return successResponse("Cart fetched", cart)
    except Exception as ex:
        print("exception under Cart controller:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))

async def get_cart_by_id(cart_id: str, cartCollection):
    cart = await CartEntity.find_one_cart_by_id(cart_id, cartCollection)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart.dict()

async def delete_cart(cart_id: str, cartCollection):
    if not await CartEntity.delete_cart(cart_id, cartCollection):
        raise HTTPException(status_code=404, detail="Cart not found")
    return {"deleted": True}
