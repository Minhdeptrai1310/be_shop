from fastapi import APIRouter, Depends, Path, Body
from models.cartModel import (
    CartResponseSchema,
    CartCreateSchema,
    GetAllCartResponseSchema
)
from database.collections import (
    get_cart_collection
)
from controllers.cartController import (
    get_all_carts_by_userId,
    create_cart,
    delete_cart,
    update_cart
)

cart = APIRouter()

@cart.get('/{user_id}', response_model=GetAllCartResponseSchema)
async def get_all_cart_by_userId(user_id: str = Path(...), cartCollection=Depends(get_cart_collection)):
    return await get_all_carts_by_userId(user_id, cartCollection)

@cart.post('/', response_model=CartResponseSchema)
async def create_cart_route(payload: CartCreateSchema, cartCollection=Depends(get_cart_collection)):
    return await create_cart(payload, cartCollection)

@cart.put('/{id}')
async def update_cart_route(id: str = Path(...), payload: CartCreateSchema = Body(...), cartCollection=Depends(get_cart_collection)):
    return await update_cart(id, payload, cartCollection)

@cart.delete('/{id}')
async def delete_cart_route(id: str = Path(...), cartCollection=Depends(get_cart_collection)):
    return await delete_cart(id, cartCollection)