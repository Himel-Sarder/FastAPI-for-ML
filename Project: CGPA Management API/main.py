import json
from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel, Field, computed_field
from typing import Annotated
from starlette.responses import JSONResponse

app = FastAPI(title="CGPA Management API")


# ---------------------- STUDENT MODEL ----------------------
class Student(BaseModel):
    student_id: Annotated[int, Field(..., description='ID of the student', examples=[101])]
    name: Annotated[str, Field(..., description='Name of the student')]

    subject1: str
    credit1: Annotated[int, Field(..., gt=0, le=4)]
    grade_point1: Annotated[float, Field(..., ge=0.0, le=4.0)]

    subject2: str
    credit2: Annotated[int, Field(..., gt=0, le=4)]
    grade_point2: Annotated[float, Field(..., ge=0.0, le=4.0)]

    subject3: str
    credit3: Annotated[int, Field(..., gt=0, le=4)]
    grade_point3: Annotated[float, Field(..., ge=0.0, le=4.0)]

    # ---------------------- HELPER FUNCTION ----------------------
    def point_to_grade(self, point: float) -> str:
        if point >= 4.00:
            return "A+"
        elif point >= 3.75:
            return "A"
        elif point >= 3.50:
            return "A-"
        elif point >= 3.25:
            return "B+"
        elif point >= 3.00:
            return "B"
        elif point >= 2.75:
            return "B-"
        elif point >= 2.50:
            return "C+"
        elif point >= 2.00:
            return "C"
        else:
            return "F"

    # ---------------------- INDIVIDUAL COURSE GRADES ----------------------
    @computed_field
    @property
    def grade1(self) -> str:
        return self.point_to_grade(self.grade_point1)

    @computed_field
    @property
    def grade2(self) -> str:
        return self.point_to_grade(self.grade_point2)

    @computed_field
    @property
    def grade3(self) -> str:
        return self.point_to_grade(self.grade_point3)

    # ---------------------- CGPA CALCULATION ----------------------
    @computed_field
    @property
    def cgpa(self) -> float:
        total_points = (
            self.credit1 * self.grade_point1 +
            self.credit2 * self.grade_point2 +
            self.credit3 * self.grade_point3
        )
        total_credits = self.credit1 + self.credit2 + self.credit3
        return round(total_points / total_credits, 2)

    # ---------------------- OVERALL CGPA GRADE ----------------------
    @computed_field
    @property
    def grade(self) -> str:
        return self.point_to_grade(self.cgpa)


# ---------------------- HELPER FUNCTIONS ----------------------
def load_data():
    try:
        with open('students.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data


def save_data(data):
    with open('students.json', 'w') as f:
        json.dump(data, f, indent=4)


# ---------------------- ROUTES ----------------------
@app.get("/")
def hello():
    return {'message': 'CGPA Management API'}


@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage CGPA of students'}


@app.get('/view')
def view():
    data = load_data()
    return list(data.values())


@app.get('/student/{student_id}')
def view_student(student_id: int = Path(..., description='ID of the student')):
    data = load_data()
    student = data.get(str(student_id))
    if not student:
        raise HTTPException(status_code=404, detail='Student not found')
    return student


@app.get('/sort')
def sort_student(
    sort_by: str = Query(..., description='Field to sort by, e.g., cgpa, grade_point1, grade1'),
    order: str = Query('asc', description='Sort order: asc or desc')
):
    valid_fields = ["cgpa", "grade_point1", "grade_point2", "grade_point3", "grade1", "grade2", "grade3"]
    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid field, select from {valid_fields}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid order, select 'asc' or 'desc'"
        )

    data = load_data()
    sort_order = True if order == "desc" else False

    # Sorting
    def sort_key(x):
        val = x.get(sort_by)
        # For grade fields, convert letter grade to numeric for sorting
        if sort_by in ["grade1", "grade2", "grade3"]:
            grade_map = {"A+": 4.0, "A": 3.75, "A-": 3.5, "B+": 3.25, "B": 3.0, "B-": 2.75, "C+": 2.5, "C": 2.0, "F": 0}
            val = grade_map.get(val, 0)
        return val

    sorted_data = sorted(data.values(), key=sort_key, reverse=sort_order)
    return sorted_data


@app.post('/create')
def create_student(student: Student):
    data = load_data()

    if str(student.student_id) in data:
        raise HTTPException(status_code=400, detail='Student already exists')

    student_data = student.model_dump()
    # Computed fields
    student_data['cgpa'] = student.cgpa
    student_data['grade'] = student.grade
    student_data['grade1'] = student.grade1
    student_data['grade2'] = student.grade2
    student_data['grade3'] = student.grade3

    data[str(student.student_id)] = student_data
    save_data(data)

    return JSONResponse(
        status_code=201,
        content={'message': 'Student created successfully', 'student': student_data}
    )

from typing import Optional

class StudentUpdate(BaseModel):
    name: Optional[str] = None

    subject1: Optional[str] = None
    credit1: Optional[int] = Field(default=None, gt=0, le=4)
    grade_point1: Optional[float] = Field(default=None, ge=0.0, le=4.0)

    subject2: Optional[str] = None
    credit2: Optional[int] = Field(default=None, gt=0, le=4)
    grade_point2: Optional[float] = Field(default=None, ge=0.0, le=4.0)

    subject3: Optional[str] = None
    credit3: Optional[int] = Field(default=None, gt=0, le=4)
    grade_point3: Optional[float] = Field(default=None, ge=0.0, le=4.0)


@app.put("/update/{student_id}")
def update_student(
    student_id: int = Path(..., description="ID of the student to update"),
    student_update: StudentUpdate = None
):
    data = load_data()
    str_id = str(student_id)

    if str_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")

    # Existing student data
    existing_student_info = data[str_id]

    # Only updated fields
    updated_fields = student_update.model_dump(exclude_unset=True)

    # Merge old + new
    for key, value in updated_fields.items():
        existing_student_info[key] = value

    # Recalculate computed fields
    existing_student_info['student_id'] = student_id
    student_obj = Student(**existing_student_info)

    updated_data = student_obj.model_dump()

    # Save updated data
    data[str_id] = updated_data
    save_data(data)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Student updated successfully",
            "student": updated_data
        }
    )


@app.delete('/delete/{student_id}')
def delete_student(student_id: str):
    # load data
    data = load_data()

    if student_id not in data:
        raise HTTPException(status_code=404, detail='Student not found')

    del data[student_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'Student deleted'})