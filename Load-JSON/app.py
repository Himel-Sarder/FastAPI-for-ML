import json
from fastapi import FastAPI


app = FastAPI()

def load_data():
    with open('bookings.json', 'r') as d:
        data = json.load(d)
        return data

# Root route
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Path parameter
@app.get("/user/{name}")
def read_user(name: str):
    return {"Hello": name}

# Query parameter
@app.get("/add")
def add_numbers(a: int, b: int):
    return {"result": a + b}

@app.get('/view')
def view():
    data = load_data()
    return data