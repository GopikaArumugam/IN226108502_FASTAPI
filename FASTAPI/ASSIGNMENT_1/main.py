from fastapi import FastAPI

app = FastAPI()

# ===== Products List (Task 1: exactly 7 products) =====
products = [
    {"id": 1, "name": "Mouse", "price": 20, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 30, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 150, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 5, "category": "Accessories", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]

# ===== 1️⃣ Get all products =====
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

# ===== 2️⃣ Filter products by category =====
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered:
        return {"error": "No products found in this category"}
    return {"products": filtered, "total": len(filtered)}

# ===== 3️⃣ Show only in-stock products =====
@app.get("/products/instock")
def get_instock_products():
    in_stock_products = [p for p in products if p["in_stock"]]
    return {"in_stock_products": in_stock_products, "count": len(in_stock_products)}

# ===== 4️⃣ Store summary =====
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

# ===== 5️⃣ Search products by name =====
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched = [p for p in products if keyword.lower() in p["name"].lower()]
    if not matched:
        return {"message": "No products matched your search"}
    return {"matched_products": matched, "total_matches": len(matched)}