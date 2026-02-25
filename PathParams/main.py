import json
from fastapi import FastAPI, Path

app = FastAPI()

# ------------------------------
# Load users with scores
# ------------------------------
def load_data():
    with open('users.json', 'r') as d:
        return json.load(d)

data = load_data()

# ------------------------------
# Route 1: View all users
# ------------------------------
@app.get("/view")
def view():
    return data

# ------------------------------
# Route 2: Get user by ID
# ------------------------------
@app.get("/check/{user_id}")
def view_user(
    user_id: int = Path(
        ...,
        description="ID of User",
        example = 103
    )
):
    for user in data:
        if user["id"] == user_id:
            return user
    return {"error": "User not found!"}

# ------------------------------
# Route 3: Get users by department
# ------------------------------
@app.get("/department/{dept_name}")
def users_by_department(
    dept_name: str = Path(
        ...,
        description="Department name",
        example = 'CSE'
    )
):
    dept_users = [u for u in data if u["department"] == dept_name]
    if dept_users:
        return dept_users
    return {"error": "No users found in this department"}

# ------------------------------
# Route 4: Get users with score >= min_score
# ------------------------------
@app.get("/score/{min_score}")
def users_with_min_score(
    min_score: int = Path(
        ...,
        description="Minimum score to filter users",
        ge=0,
        le=100,
        example = 95
    )
):
    high_scorers = [u for u in data if u["score"] >= min_score]
    if high_scorers:
        return high_scorers
    return {"error": f"No users with score >= {min_score}"}

# ------------------------------
# Route 5: Get user by department and ID
# ------------------------------
@app.get("/users/{department}/{user_id}")
def get_user_by_department(
    department: str = Path(
        ...,
        description="Department name",
        example = 'CSE'
    ),
    user_id: int = Path(
        ...,
        description="User ID",
        example = 102
    )
):
    for user in data:
        if user["id"] == user_id and user["department"] == department:
            return user
    return {"error": "User not found!"}