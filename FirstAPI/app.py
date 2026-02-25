from fastapi import FastAPI

app = FastAPI()

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