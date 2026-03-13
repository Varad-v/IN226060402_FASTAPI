from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# Product Model
# -----------------------------
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# -----------------------------
# Initial Products List
# -----------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]


# -----------------------------
# Helper function
# -----------------------------
def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


# -----------------------------
# GET all products
# -----------------------------
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# -----------------------------
# POST add product
# -----------------------------
@app.post("/products")
def add_product(new_product: NewProduct, response: Response):

    for p in products:
        if p["name"].lower() == new_product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product with this name already exists"}

    next_id = max(p["id"] for p in products) + 1

    product_dict = {
        "id": next_id,
        "name": new_product.name,
        "price": new_product.price,
        "category": new_product.category,
        "in_stock": new_product.in_stock
    }

    products.append(product_dict)

    response.status_code = status.HTTP_201_CREATED
    return {
        "message": "Product added",
        "product": product_dict
    }


# -----------------------------
# PUT update product
# -----------------------------
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: int = None,
    in_stock: bool = None,
    response: Response = None
):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {
        "message": "Product updated",
        "product": product
    }


# -----------------------------
# DELETE product
# -----------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}


# -----------------------------
# GET audit summary
# MUST BE ABOVE /products/{product_id}
# -----------------------------
@app.get("/products/audit")
def product_audit():

    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }


# -----------------------------
# GET product by ID
# -----------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product