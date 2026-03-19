from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()

# -----------------------------
# Sample Data
# -----------------------------
cars = [
    {"id": 1, "name": "Swift", "brand": "Maruti", "price_per_day": 1500, "fuel_type": "Petrol", "is_available": True},
    {"id": 2, "name": "Creta", "brand": "Hyundai", "price_per_day": 2500, "fuel_type": "Diesel", "is_available": True},
    {"id": 3, "name": "City", "brand": "Honda", "price_per_day": 2200, "fuel_type": "Petrol", "is_available": False},
    {"id": 4, "name": "Thar", "brand": "Mahindra", "price_per_day": 3000, "fuel_type": "Diesel", "is_available": True},
]

rentals = []
rental_counter = 1

# -----------------------------
# Helper Functions
# -----------------------------
def find_car(car_id):
    for car in cars:
        if car["id"] == car_id:
            return car
    return None

def calculate_rent(price, days):
    return price * days

def filter_cars_logic(brand, max_price, fuel_type, is_available):
    result = cars

    if brand is not None:
        result = [c for c in result if c["brand"].lower() == brand.lower()]

    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]

    if fuel_type is not None:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]

    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    return result

# -----------------------------
# Models
# -----------------------------
class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=30)

class NewCar(BaseModel):
    name: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    price_per_day: int = Field(..., gt=0)
    fuel_type: str
    is_available: bool = True

class CheckoutRequest(BaseModel):
    customer_name: str
    days: int

# -----------------------------
# Q1 - Home
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to Car Rental Service 🚗"}

# -----------------------------
# Q2 - Get all cars
# -----------------------------
@app.get("/cars")
def get_cars():
    return {"total": len(cars), "cars": cars}

# -----------------------------
# Q5 - Summary (IMPORTANT ORDER)
# -----------------------------
@app.get("/cars/summary")
def summary():
    available = [c for c in cars if c["is_available"]]
    return {
        "total": len(cars),
        "available": len(available),
        "unavailable": len(cars) - len(available)
    }

# -----------------------------
# Q10 - Filter
# -----------------------------
@app.get("/cars/filter")
def filter_cars(
    brand: Optional[str] = None,
    max_price: Optional[int] = None,
    fuel_type: Optional[str] = None,
    is_available: Optional[bool] = None
):
    result = filter_cars_logic(brand, max_price, fuel_type, is_available)
    return {"count": len(result), "cars": result}

# -----------------------------
# Q16 - Search
# -----------------------------
@app.get("/cars/search")
def search(keyword: str):
    result = [c for c in cars if keyword.lower() in c["name"].lower() or keyword.lower() in c["brand"].lower()]
    if not result:
        return {"message": "No cars found"}
    return {"count": len(result), "cars": result}

# -----------------------------
# Q17 - Sort
# -----------------------------
@app.get("/cars/sort")
def sort(sort_by: str = "price_per_day", order: str = "asc"):
    if sort_by not in ["price_per_day", "name", "brand"]:
        return {"error": "Invalid sort field"}

    reverse = True if order == "desc" else False

    sorted_list = sorted(cars, key=lambda x: x[sort_by], reverse=reverse)
    return {"cars": sorted_list}

# -----------------------------
# Q18 - Pagination
# -----------------------------
@app.get("/cars/page")
def paginate(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    data = cars[start:start + limit]

    total_pages = math.ceil(len(cars) / limit)

    return {
        "page": page,
        "limit": limit,
        "total": len(cars),
        "total_pages": total_pages,
        "cars": data
    }

# -----------------------------
# Q20 - Combined
# -----------------------------
@app.get("/cars/browse")
def browse(
    keyword: Optional[str] = None,
    sort_by: str = "price_per_day",
    order: str = "asc",
    page: int = 1,
    limit: int = 2
):
    result = cars

    if keyword:
        result = [c for c in result if keyword.lower() in c["name"].lower()]

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    paginated = result[start:start + limit]

    return {
        "total": len(result),
        "page": page,
        "cars": paginated
    }

# -----------------------------
# Q3 - Get by ID (LAST)
# -----------------------------
@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}
    return car

# -----------------------------
# Q4 - Rentals list
# -----------------------------
@app.get("/rentals")
def get_rentals():
    return {"total": len(rentals), "rentals": rentals}

# -----------------------------
# Q8 - Rent Car
# -----------------------------
@app.post("/rent")
def rent(data: RentalRequest):
    global rental_counter

    car = find_car(data.car_id)
    if not car:
        return {"error": "Car not found"}

    if not car["is_available"]:
        return {"error": "Car not available"}

    total = calculate_rent(car["price_per_day"], data.days)

    rental = {
        "rental_id": rental_counter,
        "customer_name": data.customer_name,
        "car_name": car["name"],
        "days": data.days,
        "total_price": total
    }

    rentals.append(rental)
    rental_counter += 1
    car["is_available"] = False

    return rental

# -----------------------------
# Q11 - Add Car
# -----------------------------
@app.post("/cars")
def add_car(new_car: NewCar, response: Response):
    for c in cars:
        if c["name"].lower() == new_car.name.lower():
            return {"error": "Duplicate car"}

    car = new_car.dict()
    car["id"] = len(cars) + 1

    cars.append(car)
    response.status_code = 201

    return car

# -----------------------------
# Q12 - Update Car
# -----------------------------
@app.put("/cars/{car_id}")
def update_car(car_id: int, price: Optional[int] = None, is_available: Optional[bool] = None):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}

    if price is not None:
        car["price_per_day"] = price

    if is_available is not None:
        car["is_available"] = is_available

    return car

# -----------------------------
# Q13 - Delete Car
# -----------------------------
@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}

    cars.remove(car)
    return {"message": "Deleted successfully"}

# -----------------------------
# Q15 - Return Car (Workflow)
# -----------------------------
@app.post("/return/{car_id}")
def return_car(car_id: int):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}

    car["is_available"] = True
    return {"message": "Car returned successfully"}