from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
from pymongo import MongoClient

# MongoDB connection URI
MONGODB_URI =  "mongodb+srv://Yogesh:12345@cluster0.bmkp6gc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# # Connect to MongoDB
# client = MongoClient(MONGODB_URI)
# db = client["library_management"]
# students_collection = db["students"]

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client["library_management"]
    students_collection = db["students"]
    # Check if MongoDB is connected
    if client.server_info():
        print("Connected to MongoDB successfully")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# FastAPI app instance
app = FastAPI()


class Address(BaseModel):
    city: str
    country: str


class Student(BaseModel):
    name: str
    age: int
    address: Address


@app.post("/students", status_code=201)
async def create_student(student: Student):
    student_data = student.model_dump()
    inserted_student = students_collection.insert_one(student_data)
    return {"id": str(inserted_student.inserted_id)}


@app.get("/students", status_code=200)
async def list_students(country: str = Query(None), age: int = Query(None)):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = list(students_collection.find(query, {"_id": 0}))
    return {"data": students}


@app.get("/students/{id}", status_code=200)
async def get_student(id: str = Path(...)):
    student = students_collection.find_one({"_id": id}, {"_id": 0})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")


@app.patch("/students/{id}", status_code=204)
async def update_student(student: Student,id: str = Path(...)):
    student_data = student.model_dump(exclude_unset=True)
    updated_student = students_collection.update_one({"_id": id}, {"$set": student_data})
    if updated_student.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return

# @app.patch("/students/{id}", status_code=204)
# async def update_student(student: Student,id: str = Path(...)):
#     student_data = student.model_dump(exclude_unset=True)
#     updated_student = students_collection.update_one({"_id": id}, {"$set": student_data})
#     if updated_student.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Student not found")
#     return


@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str = Path(...)):
    deleted_student = students_collection.delete_one({"_id": id})
    if deleted_student.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return
