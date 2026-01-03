from models.orderModel import OrderCreateSchema
from database.collections import get_user_collection, get_order_collection, get_cart_collection, get_product_collection, get_order_items_collection, get_mail_collection
from fastapi import APIRouter, Depends, Path
from controllers.orderController import check_out_and_send_mail, get_all_orders_controller, confirm_payment_controller

order = APIRouter()

@order.post('/check-out')
async def checkOut(
        payload: OrderCreateSchema, 
        orderCollection = Depends(get_order_collection), 
        cartCollection = Depends(get_cart_collection), 
        productCollection = Depends(get_product_collection),
        orderItemsCollection = Depends(get_order_items_collection),
        userCollection = Depends(get_user_collection),
        emailCollection = Depends(get_mail_collection)
    ):
    return await check_out_and_send_mail(
        payload=payload,
        db=orderCollection, 
        cart_db = cartCollection, 
        product_db = productCollection, 
        order_item_db = orderItemsCollection,
        user_db = userCollection,
        email_db = emailCollection
    )

@order.get('/')
async def getAllOrders(
    orderCollection = Depends(get_order_collection),
    orderItemsCollection = Depends(get_order_items_collection),
    userCollection = Depends(get_user_collection)
):
    return await get_all_orders_controller(orderCollection, orderItemsCollection, userCollection)

@order.post('/{id}/confirm_payment')
async def confirmPayment(
    id: str = Path(...),
    orderCollection = Depends(get_order_collection),
    orderItemsCollection = Depends(get_order_items_collection),
    userCollection = Depends(get_user_collection),
    emailCollection = Depends(get_mail_collection)
):
    return await confirm_payment_controller(id, orderCollection, orderItemsCollection, userCollection, emailCollection)