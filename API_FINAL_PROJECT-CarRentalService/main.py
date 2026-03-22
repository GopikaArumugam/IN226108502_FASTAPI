from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

cars = []
customers = []
bookings = []

car_id_counter = 1
customer_id_counter = 1
booking_id_counter = 1


# ------------------ MODELS ------------------

class Car(BaseModel):
    name: str = Field(..., min_length=2)
    brand: str
    price_per_day: float = Field(..., gt=0)
    available: bool = True


class Customer(BaseModel):
    name: str
    license_number: str


class Booking(BaseModel):
    customer_id: int
    car_id: int
    days: int = Field(..., gt=0)


# ------------------ HELPER FUNCTIONS ------------------

def find_car(car_id: int):
    for car in cars:
        if car["id"] == car_id:
            return car
    return None


def find_customer(customer_id: int):
    for customer in customers:
        if customer["id"] == customer_id:
            return customer
    return None


def find_booking(booking_id: int):
    for booking in bookings:
        if booking["id"] == booking_id:
            return booking
    return None


def calculate_total(price, days):
    return price * days


# ------------------ DAY 1-2 (GET APIs) ------------------

@app.get("/")
def home():
    return {"message": "Car Rental Service API Running"}


@app.get("/cars")
def get_cars(sort: Optional[str] = None, page: int = 1, limit: int = 5):
    data = cars.copy()

    if sort == "price":
        data.sort(key=lambda x: x["price_per_day"])
    elif sort == "name":
        data.sort(key=lambda x: x["name"])

    start = (page - 1) * limit
    end = start + limit

    return data[start:end]


@app.get("/cars/count")
def count_cars():
    return {"total_cars": len(cars)}


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


# ------------------ DAY 3 (POST APIs) ------------------

@app.post("/cars", status_code=201)
def add_car(car: Car):
    global car_id_counter
    new_car = car.dict()
    new_car["id"] = car_id_counter
    cars.append(new_car)
    car_id_counter += 1
    return new_car


@app.post("/customers", status_code=201)
def add_customer(customer: Customer):
    global customer_id_counter
    new_customer = customer.dict()
    new_customer["id"] = customer_id_counter
    customers.append(new_customer)
    customer_id_counter += 1
    return new_customer


# ------------------ DAY 4 (CRUD) ------------------

@app.put("/cars/{car_id}")
def update_car(car_id: int, updated_car: Car):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    car.update(updated_car.dict())
    return car


@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    cars.remove(car)
    return {"message": "Car deleted"}


@app.get("/customers")
def get_customers():
    return customers


# ------------------ DAY 5 (MULTI-STEP WORKFLOW) ------------------

@app.post("/book", status_code=201)
def book_car(booking: Booking):
    global booking_id_counter

    car = find_car(booking.car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if not car["available"]:
        raise HTTPException(status_code=400, detail="Car not available")

    customer = find_customer(booking.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    total_price = calculate_total(car["price_per_day"], booking.days)

    new_booking = {
        "id": booking_id_counter,
        "customer_id": booking.customer_id,
        "car_id": booking.car_id,
        "days": booking.days,
        "total_price": total_price,
        "status": "booked"
    }

    bookings.append(new_booking)
    booking_id_counter += 1

    car["available"] = False

    return new_booking


@app.put("/return/{booking_id}")
def return_car(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking["status"] == "returned":
        raise HTTPException(status_code=400, detail="Already returned")

    car = find_car(booking["car_id"])
    car["available"] = True

    booking["status"] = "returned"

    return {"message": "Car returned successfully"}


@app.get("/bookings")
def get_bookings():
    return bookings


# ------------------ DAY 6 (ADVANCED APIs) ------------------

@app.get("/cars/search")
def search_cars(name: Optional[str] = None):
    result = cars

    if name is not None:
        result = [car for car in result if name.lower() in car["name"].lower()]

    return result


@app.get("/cars/brand/{brand}")
def filter_by_brand(brand: str):
    return [car for car in cars if car["brand"].lower() == brand.lower()]


@app.get("/cars/browse")
def browse_cars(
    name: Optional[str] = None,
    sort: Optional[str] = None,
    page: int = 1,
    limit: int = 5
):
    result = cars

    if name:
        result = [car for car in result if name.lower() in car["name"].lower()]

    if sort == "price":
        result.sort(key=lambda x: x["price_per_day"])

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]