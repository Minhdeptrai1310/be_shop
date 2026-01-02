from bson.objectid import ObjectId

class OrderItemEntity:

    @staticmethod
    async def create_many(order_id: ObjectId, cart_items: list, db):
        docs = []
        for item in cart_items:
            docs.append({
                "orderId": order_id,
                "productId": item["productId"],
                "size": item["size"],
                "color": item["color"],
                "quantity": item["quantity"],
                "price": item["price"]
            })

        if docs:
            db.insert_many(docs)
