import uuid

def generate_order_code():
    return f"DH-{uuid.uuid4().hex[:8].upper()}"
