from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {"id": 1, "name": "Mouse", "price": 20, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 30, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 150, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 5, "category": "Accessories", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]

# Day 1 Task - Get all products
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

# Day 1 Task - Filter products by category
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered:
        return {"error": "No products found in this category"}
    return {"products": filtered, "total": len(filtered)}

# Day 1 Task - Show in-stock products
@app.get("/products/instock")
def get_instock_products():
    in_stock_products = [p for p in products if p["in_stock"]]
    return {"in_stock_products": in_stock_products, "count": len(in_stock_products)}

# Day 1 Task - Store summary
@app.get("/store/summary")
def get_store_summary():
    total = len(products)
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = total - in_stock_count
    categories = list(set([p["category"] for p in products]))
    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": categories
    }

# Day 1 Task - Search products by name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched = [p for p in products if keyword.lower() in p["name"].lower()]
    if not matched:
        return {"message": "No products matched your search"}
    return {"matched_products": matched, "total_matches": len(matched)}

# Day 2 Task 1 - Filter products using query parameters
@app.get("/products/filter")
def filter_products(category: str = None, min_price: int = None, max_price: int = None):
    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    return {"products": result, "total": len(result)}

# Day 2 Task 2 - Get only name and price of a product
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}
    return {"error": "Product not found"}

# Day 2 Task 3 - Customer feedback with Pydantic validation
feedback = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def add_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

# Day 2 Task 4 - Product summary dashboard
@app.get("/products/summary")
def product_summary():
    total = len(products)
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = total - in_stock_count

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {"name": most_expensive["name"], "price": most_expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }

# Day 2 Task 5 - Bulk order validation and processing
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]

@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# Bonus Task - Order status tracking system
orders = []

@app.post("/orders")
def create_order(order: dict):
    order["id"] = len(orders) + 1
    order["status"] = "pending"
    orders.append(order)
    return order

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for o in orders:
        if o["id"] == order_id:
            return o
    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for o in orders:
        if o["id"] == order_id:
            o["status"] = "confirmed"
            return o
    return {"error": "Order not found"}