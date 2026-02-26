import json
from fastapi import FastAPI, Query, HTTPException

app = FastAPI()

def load_data():
    with open("users.json", "r") as f:
        return json.load(f)

data = load_data()

# --------------------------------
# Get user by ID using Query param
# --------------------------------
@app.get("/check")
def view_user(
    user_id: int = Query(
        ...,
        description="ID of the user",
        example = 102
    )
):
    for user in data:
        if user["id"] == user_id:
            return user
    return {"error": "User not found!"}


# --------------------------------
# Sort users by score
# --------------------------------
@app.get("/sort")
def sort_users(
    order: str = Query(
        "asc",
        description="Sort order: asc (low to high) or desc (high to low)",
        example='asc'
    )
):
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail='Please Select from acs or desc') # <-- Bad Request

    sorted_users = sorted(
        data,
        key=lambda x: x["score"],
        reverse=True if order == "desc" else False
    )

    return sorted_users

@app.get("/filter")
def filter_users(
    department: str = Query(
        None,
        description="Filter by department",
        example = 'CSE'
    )
):
    if department:
        return [u for u in data if u["department"] == department]
    return data