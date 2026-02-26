import json
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


# ----------------------------
# Pydantic Model
# ----------------------------

class User(BaseModel):
    id: int
    name: str
    department: str
    score: float


# ----------------------------
# Load Data
# ----------------------------

def load_data():
    with open("users.json", "r") as f:
        return json.load(f)

data = load_data()


# --------------------------------
# Get user by ID
# --------------------------------
@app.get("/check", response_model=User)
def view_user(
    user_id: int = Query(..., description="ID of the user", example=102)
):
    for user in data:
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found!")


# --------------------------------
# Sort users by score
# --------------------------------
@app.get("/sort", response_model=List[User])
def sort_users(
    order: str = Query(
        "asc",
        pattern="^(asc|desc)$",   # <-- Pydantic validation
        description="Sort order: asc or desc"
    )
):
    sorted_users = sorted(
        data,
        key=lambda x: x["score"],
        reverse=True if order == "desc" else False
    )

    return sorted_users


# --------------------------------
# Filter users by department
# --------------------------------
@app.get("/filter", response_model=List[User])
def filter_users(
    department: Optional[str] = Query(
        None,
        description="Filter by department",
        example="CSE"
    )
):
    if department:
        return [u for u in data if u["department"] == department]

    return data