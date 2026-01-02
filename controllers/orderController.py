from fastapi import HTTPException
from bson.objectid import ObjectId

from database.entity.orderEntity import OrderEntity
from database.entity.userEntity import User
from database.entity.orderItemEntity import OrderItemEntity
from models.orderModel import OrderCreateSchema
from util.order_code import generate_order_code
from jinja2 import Environment, FileSystemLoader
from controllers.emailController import send_mail, SendMailDTO

async def check_out(payload: OrderCreateSchema, db, cart_db, product_db, order_item_db, user_db):
    userId = payload.userId
    paymentMethod = payload.paymentMethod
    address = payload.address
    # 0. Lay userinfo
    user_info = await User.find_one_user_by_id(userId, user_db)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    # 1. Lấy cart
    cart_items = list(cart_db.find({"userId": userId}))
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 2. Snapshot giá + tính tổng tiền
    total_amount = 0
    snapshot_items = []

    for item in cart_items:
        product = product_db.find_one({"_id": ObjectId(item["productId"])})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        price = product.get("salePrice") or product["price"]
        total_amount += price * item["quantity"]

        snapshot_items.append({
            "productId": item["productId"],
            "size": item["size"],
            "color": item["color"],
            "quantity": item["quantity"],
            "price": price
        })

    # 3. Tạo order
    order = await OrderEntity.create_order(
        userId=userId,
        totalAmount=total_amount,
        paymentMethod=paymentMethod,
        orderCode=generate_order_code(),
        address=address,
        orderEntity=db
    )

    # 4. Tạo order_items
    await OrderItemEntity.create_many(
        ObjectId(order.id),
        snapshot_items,
        order_item_db
    )

    # 5. Clear cart (BẮT BUỘC)
    cart_db.delete_many({"userId": userId})

    # 6. Load lại order + items để trả response
    full_order = await OrderEntity.find_order_by_id(order.id, db, order_item_db)

    return {
        "success": True,
        "message": "Checkout successfully. Waiting for payment.",
        "data": {
            "id": full_order.id,
            "userId": full_order.userId,
            "orderCode": full_order.orderCode,
            "totalAmount": full_order.totalAmount,
            "status": full_order.status,
            "paymentMethod": full_order.paymentMethod,
            "address": full_order.address,
            "paidAt": int(full_order.paidAt.timestamp()) if full_order.paidAt else None,
            "orderItems": [
                {
                    "id": item.id,
                    "orderId": item.orderId,
                    "productId": item.productId,
                    "size": item.size,
                    "color": item.color,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in full_order.orderItems
            ],
            "userInfo": {
                "name": user_info.name,
                "email": user_info.email,
            }
        }
    }

async def check_out_and_send_mail(
    payload: OrderCreateSchema,
    db,
    cart_db,
    product_db,
    order_item_db,
    user_db,
    email_db
):
    checkout = await check_out(payload, db, cart_db, product_db, order_item_db, user_db)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("bank_transfer_email.html")
    html_content = template.render(**checkout["data"])

    mail_data = SendMailDTO(
        to=checkout['data']['userInfo']['email'],
        subject=f"Xác nhận đơn hàng {checkout['data']['orderCode']}",
        content=html_content
    )

    # gửi mail KHÔNG làm ảnh hưởng checkout
    try:
        await send_mail(mail_data, email_db, True)
    except Exception as e:
        print("Send mail failed:", e)

    return checkout


