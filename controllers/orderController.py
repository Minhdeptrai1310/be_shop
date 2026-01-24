from fastapi import HTTPException
from bson.objectid import ObjectId

from database.entity.orderEntity import OrderEntity
from database.entity.userEntity import User
from database.entity.orderItemEntity import OrderItemEntity
from models.orderModel import OrderCreateSchema, OrderStatusEnum
from util.order_code import generate_order_code
from jinja2 import Environment, FileSystemLoader
from controllers.emailController import send_mail, SendMailDTO
from util.ResponseSchema import successResponse, errorResponse
from datetime import datetime

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

    # 2. Snapshot giá + tính tổng tiền + kiểm tra stock
    total_amount = 0
    snapshot_items = []
    products_to_update = []  # Lưu thông tin product cần cập nhật stock

    for item in cart_items:
        product = product_db.find_one({"_id": ObjectId(item["productId"])})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Kiểm tra stock
        current_stock = product.get("stock", 0)
        requested_quantity = item["quantity"]
        
        if current_stock < requested_quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Product {product.get('name', 'Unknown')} không đủ hàng. Còn lại: {current_stock}, yêu cầu: {requested_quantity}"
            )

        price = product.get("salePrice") or product["price"]
        total_amount += price * item["quantity"]

        snapshot_items.append({
            "productId": item["productId"],
            "size": item["size"],
            "color": item["color"],
            "quantity": item["quantity"],
            "price": price
        })
        
        # Lưu thông tin để cập nhật stock
        products_to_update.append({
            "productId": item["productId"],
            "quantity": requested_quantity
        })

    # 3. Tạo order
    order = await OrderEntity.create_order(
        userId=userId,
        user_info=user_info,
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

    # 4.5. Trừ stock của các sản phẩm (gộp quantity cho cùng productId)
    product_stock_updates = {}
    for product_update in products_to_update:
        product_id = product_update["productId"]
        if product_id in product_stock_updates:
            product_stock_updates[product_id] += product_update["quantity"]
        else:
            product_stock_updates[product_id] = product_update["quantity"]
    
    # Cập nhật stock cho từng product
    for product_id_str, total_quantity in product_stock_updates.items():
        product_id = ObjectId(product_id_str)
        
        result = product_db.update_one(
            {"_id": product_id},
            {
                "$inc": {"stock": -total_quantity},
                "$set": {"updatedAt": datetime.now()}
            }
        )
        
        if result.matched_count == 0:
            # Nếu không tìm thấy product, có thể đã bị xóa - log warning
            print(f"Warning: Product {product_id} not found when updating stock")
        elif result.modified_count == 0:
            print(f"Warning: Stock not updated for product {product_id}")

    # 5. Clear cart (BẮT BUỘC)
    cart_db.delete_many({"userId": userId})

    # 6. Load lại order + items để trả response
    full_order = await OrderEntity.find_order_by_id(order.id, db, order_item_db, user_db)

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

async def get_all_orders_controller(order_db, order_item_db, user_db):
    all_orders = await OrderEntity.get_all_orders(order_db, order_item_db, user_db)
    return successResponse("All Orders Fetched", all_orders)

async def get_order_by_user_id_controller(user_id, order_db, order_item_db, user_db):
    orders = await OrderEntity.get_orders_by_user_id(user_id, order_db, order_item_db, user_db)
    return successResponse("Orders Fetched", orders)

async def confirm_payment_controller(order_id, order_db, order_item_db, user_db, email_db):
    confirm = await OrderEntity.confirm_payment(order_id, order_db, order_item_db, user_db)
    print(confirm)
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("confirm_payment_email.html")
    html_content = template.render(confirm)

    mail_data = SendMailDTO(
        to=confirm.user_info.email,
        subject=f"Xác nhận thanh toán đơn hàng {confirm.orderCode}",
        content=html_content
    )

    try:
        await send_mail(mail_data, email_db, True)
    except Exception as e:
        print("Send mail failed:", e)

    return successResponse("Confirmed order", confirm)

async def cancel_order_controller(order_id, order_db, order_item_db, product_db, user_db):
    """
    Hủy đơn hàng và hoàn lại stock cho các sản phẩm
    Chỉ hủy được nếu đơn hàng chưa thanh toán (PENDING_PAYMENT hoặc EXPIRED)
    """
    # 1. Lấy thông tin đơn hàng
    order = await OrderEntity.find_order_by_id(order_id, order_db, order_item_db, user_db)
    
    # 2. Kiểm tra trạng thái - chỉ hủy được nếu chưa thanh toán
    if order.status not in [OrderStatusEnum.PENDING_PAYMENT, OrderStatusEnum.EXPIRED]:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể hủy đơn hàng. Đơn hàng đang ở trạng thái: {order.status}"
        )
    
    # 3. Hủy đơn hàng (cập nhật status)
    await OrderEntity.cancel_order(order_id, order_db)
    
    # 4. Hoàn lại stock cho các sản phẩm
    # Gộp quantity cho cùng productId
    product_stock_returns = {}
    for item in order.orderItems:
        product_id = item.productId
        if product_id in product_stock_returns:
            product_stock_returns[product_id] += item.quantity
        else:
            product_stock_returns[product_id] = item.quantity
    
    # Cập nhật stock cho từng product
    for product_id_str, total_quantity in product_stock_returns.items():
        product_id = ObjectId(product_id_str)
        
        result = product_db.update_one(
            {"_id": product_id},
            {
                "$inc": {"stock": total_quantity},
                "$set": {"updatedAt": datetime.now()}
            }
        )
        
        if result.matched_count == 0:
            print(f"Warning: Product {product_id} not found when returning stock")
        elif result.modified_count == 0:
            print(f"Warning: Stock not updated for product {product_id}")
    
    # 5. Load lại order để trả response
    cancelled_order = await OrderEntity.find_order_by_id(order_id, order_db, order_item_db, user_db)
    
    return successResponse(
        f"Đơn hàng {cancelled_order.orderCode} đã được hủy thành công",
        {
            "id": cancelled_order.id,
            "orderCode": cancelled_order.orderCode,
            "status": cancelled_order.status,
            "totalAmount": cancelled_order.totalAmount
        }
    )

