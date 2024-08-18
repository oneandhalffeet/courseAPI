import json
from fastapi import FastAPI, Query, HTTPException, Body
from pymongo import MongoClient
from model import Course, Chapter, CourseListResponse, CourseOverviewResponse, ChapterInfoResponse, RatingRequest
from typing import Optional
from contextlib import asynccontextmanager
import aiofiles



client = MongoClient('mongodb://localhost:27017')
db = client['kimo_db']
courses_collection = db['courses']

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
        
        # Validate and insert data into MongoDB
        for item in data:
            course = Course(**item)
            courses_collection.insert_one(course.dict())
            
        print("Data imported successfully.")
    except Exception as e:
        print(f"Error importing data: {e}")


# Example response model to get all courses
@app.get("/courses", response_model=CourseListResponse)
def get_courses(sort_by: Optional[str] = Query(None, enum=['alphabetical', 'date', 'rating']),
                domain: Optional[str] = None):
    query = {}
    if domain:
        query['domain'] = domain
    
    if sort_by:
        sort_field = {
            'alphabetical': ('name', 1),
            'date': ('date', -1),
            'rating': ('rating', -1)
        }.get(sort_by, ('name', 1))
        courses_cursor = courses_collection.find(query).sort([sort_field])
    else:
        courses_cursor = courses_collection.find(query)
    courses = [Course(**course) for course in courses_cursor]
    return {"courses": courses}

@app.get("/courses/{course_name}", response_model=CourseOverviewResponse)
def get_course_overview(course_name: str):
    course = courses_collection.find_one({"name": course_name})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"course": Course(**course)}

@app.get("/courses/{course_name}/chapters/{chapter_name}", response_model=ChapterInfoResponse)
def get_chapter_info(course_name: str, chapter_name: str):
    course = courses_collection.find_one({"name": course_name, "chapters.name": chapter_name})
    if not course or not course.get('chapters'):
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter = next((chap for chap in course['chapters'] if chap['name'] == chapter_name), None)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"chapter": Chapter(**chapter)}

@app.post("/courses/{course_name}/chapters/{chapter_name}/rate")
def rate_chapter(course_name: str, chapter_name: str, rating: RatingRequest):
    course = courses_collection.find_one_and_update(
        {"name": course_name, "chapters.name": chapter_name},
        {"$inc": {"chapters.$.rating": rating.rating, "rating": rating.rating}},
        return_document=True
    )
    if not course:
        raise HTTPException(status_code=404, detail="Chapter not found")
        
    # Calculate the new average rating for the course
    total_rating = 0
    chapter_count = len(course['chapters'])
    
    for chapter in course['chapters']:
        total_rating += chapter['rating']
    
    new_average_rating = total_rating / chapter_count if chapter_count > 0 else 0

    # Update course rating
    courses_collection.update_one(
        {"name": course_name},
        {"$set": {"rating": new_average_rating}}
    )
    return {"message": "Rating submitted", "new_rating": course['rating']}
